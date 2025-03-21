document.getElementById('uploadForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    // Create a new FormData object to send the image
    const formData = new FormData();
    const fileInput = document.getElementById('image');
    formData.append('image', fileInput.files[0]);

    try {
        // Send the image to the server
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        // Get the results div to display the data
        const resultDiv = document.getElementById('results');
        resultDiv.innerHTML = ''; // Clear previous results

        if (response.ok) {
            // Parse the JSON response
            const data = await response.json();
            const results = data.results;

            // Check if results exist and display them
            if (results && results.length > 0) {
                results.forEach(result => {
                    // Destructure the result array
                    const [ingredient, chemicalName, isHarmful, description, affectedBodyParts, harmfulnessPercentage, commonSources] = result;

                    // Create HTML content to display the results in a readable format
                    const resultHtml = `
                        <div class="result-card">
                            <h3><strong>Ingredient:</strong> ${ingredient}</h3>
                            <p><strong>Chemical Name:</strong> ${chemicalName}</p>
                            <p><strong>Is Harmful:</strong> ${isHarmful}</p>
                            <p><strong>Description:</strong> ${description}</p>
                            <p><strong>Affected Body Parts:</strong> ${affectedBodyParts}</p>
                            <p><strong>Harmfulness Percentage:</strong> ${harmfulnessPercentage}</p>
                            <p><strong>Common Sources:</strong> ${commonSources}</p>
                        </div>
                    `;
                    resultDiv.innerHTML += resultHtml; // Append the formatted HTML content
                });
            } else {
                resultDiv.innerHTML = '<p>No matching ingredients found.</p>';
            }
        } else {
            // If the response is not OK, display an error message
            const data = await response.json();
            resultDiv.innerHTML = `<p>${data.message || data.error}</p>`;
        }
    } catch (error) {
        console.error('Error:', error);
        resultDiv.innerHTML = '<p>An error occurred while processing your request.</p>';
    }
});
