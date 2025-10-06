document.getElementById('courseForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = {
        university: document.getElementById('university').value,
        major: document.getElementById('major').value,
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        credits: parseInt(document.getElementById('credits').value)
    };

    try {
        const response = await fetch('/compare', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        if (!response.ok) {
            throw new Error(await response.text());
        }
        const result = await response.json();
        document.getElementById('results').innerHTML = `
            <h2>Results</h2>
            <p><strong>Match:</strong> ${result.match_title} (${result.match_credits} credits)</p>
            <p><strong>Equivalency Score:</strong> ${result.score.toFixed(1)}%</p>
            <p>${result.recommendation}</p>
        `;
    } catch (error) {
        document.getElementById('results').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
    }
});