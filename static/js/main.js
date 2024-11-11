// feedback bericht laten zien 
function showStatus(message, isError = false) {
    const statusDiv = document.getElementById('statusMessage');
    statusDiv.textContent = message;
    statusDiv.className = `mb-6 p-4 rounded ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    statusDiv.classList.remove('hidden');
    setTimeout(() => {
        statusDiv.classList.add('hidden');
    }, 3000);
}

async function startDetection() {
    try {
        const response = await fetch('/start_detection');
        const data = await response.json();
        showStatus(data.message, data.status === 'error');
    } catch (error) {
        showStatus('Fout bij het starten van detectie', true);
    }
}


async function stopDetection() {
    try {
        const response = await fetch('/stop_detection');
        const data = await response.json();
        showStatus(data.message, data.status === 'error');
    } catch (error) {
        showStatus('Fout bij het stoppen van detectie', true);
    }
}


// Functie voor de verwerking van natuurlijke taal
async function processNaturalLanguage() {
    const nlInput = document.getElementById('nlInput').value.trim();
    const detectedObjectDiv = document.getElementById('detectedObject');
    
    if (!nlInput) {
        showStatus('Voer eerst een beschrijving in', true);
        return;
    }

    try {
        const response = await fetch('/process_natural_language', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: nlInput })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            detectedObjectDiv.textContent = `Gedetecteerd object: ${data.detected_object}`;
            showStatus(`Zoeken naar: ${data.detected_object}`, false);
            
            // Automatisch het object instellen als doel
            const targetResponse = await fetch(`/set_target/${encodeURIComponent(data.detected_object)}`);
            const targetData = await targetResponse.json();
            
            if (targetData.status === 'success') {
                showStatus(`Object ingesteld op: ${data.detected_object}`, false);
            }
        } else {
            showStatus(data.message, true);
        }
    } catch (error) {
        showStatus('Fout bij het verwerken van de tekst', true);
    }
}
