import React, {useState, useEffect} from "react";
import { Link } from "react-router-dom";
import { ReactTransliterate } from "react-transliterate";
import { useParams } from "react-router-dom";
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import Button from '@mui/material/Button';


export const SentenceList = (props) => {
    
    //Stores the project Id
    const projectId = useParams()['projectId'];
    //Stores the list of sentence object, where each object has the following field: sentence_id, project, original_sentence, translated_sentence, created_on
    const [sentences, setSentences] = useState([]);
    //Array used for storing the index of sentences which has changed translated_sentences
    const [changedSentences, setChangedSentences] = useState([]);
    //State use for re rendering during the change of sentence
    const [translated, setTranslated] = useState(-1);
    // Stores error message
    const [errorMessage, setErrorMessage] = useState("");

    //Reset changedSentence and translated states
    const resetState = () => {
        setChangedSentences([]);
        setTranslated(-1);
    }
    

    useEffect(() => {
        //AJAX call for getting the sentences for a project
        fetch("http://localhost:8000/wiki/" + projectId + "/sentence", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("wiki-trans-token")}`
            }
        }).then(response => {
            if (response.status == 401) {
                //If the user is not authenticated, it routes to login page.
                window.location.href = '/login';
            }
            return response.json()
        }).then(data => {
            if (data['error']) {
                //Incase we get a error response, we throw it here and store in errorMessage state
                throw Error(data['error']);
            }
            //Otherwise change the state sentence
            setSentences(data);
        }).catch((error) => setErrorMessage(error.message))
    }, []);

    //Function for patching the sentences
    const saveChanges = () => {
        //Iterate through changed sentence index
        changedSentences.forEach((id) => {
            fetch("http://localhost:8000/wiki/sentence/" + sentences[id]['sentence_id'], {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("wiki-trans-token")}`
                },
                body: JSON.stringify({
                    translated_sentence: sentences[id]['translated_sentence'],
                })
            }).then(response => {
                if (response.status == 401) {
                    //If the user is not authenticated, it routes to login page.
                    window.location.href = '/login';
                }
                return response.json()
            }).then(data => {
                if (data['error']) {
                    //Incase we get a error response, we throw it here and store in errorMessage state
                    throw Error(data['error']);
                }
                console.log(`Sentence with id ${sentences[id]['sentence_id']} updated..`)
            }).catch((error) => setErrorMessage(error.message))
        });
        resetState();
    }

    //Function that handles when the user changes the translated sentences
    const handleChange = (text, index) => {
        setTranslated(Math.abs(1 - translated)); 
        sentences[index]['translated_sentence'] = text;
        changedSentences.push(index);
    };

    //Handle sign out and redirect to login page
    const handleSignOut = (event) => {
        localStorage.clear()
        window.location.href = '/login';
    }

    return (
    <div>
        {/* Header */}
        <header className="header">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginLeft: '20px', marginRight: '20px' }}>
                <Link to="/"><ArrowBackIcon /></Link>
                <h3>{projectId}</h3>
                <Button variant="contained" onClick={saveChanges} disabled={translated === -1 ? true : false}>
                    Save Changes
                </Button>
                <Button variant="contained" onClick={handleSignOut}>
                    Sign Out
                </Button>
            </div>
        </header>
        {/* Sentences */}
        <div style={{padding: '60px'}}>
            {sentences.map((sentence, index) => 
                <div key={sentence['sentence_id']} className="sentence-container">
                    <div className="leftPane">
                        {/* Left side: Original Sentences */}
                        <p>{sentence['original_sentence']}</p>
                    </div>
                    <div className="rightPane">
                        {/* Right side: Translated sentences */}
                        {/* ReactTransliterate is used for transliterating the sentence */}
                        <ReactTransliterate
                            renderComponent={(props) => <textarea {...props} />}
                            value={sentence['translated_sentence']}
                            onChangeText={text => handleChange(text, index)}
                            lang={projectId.substring(0, 2)}
                            containerStyles={{color: "black"}}
                        />
                    </div>
                </div>
            )}
        </div>
    </div>
    );
}