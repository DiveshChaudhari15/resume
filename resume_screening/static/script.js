document.querySelector('form').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = new FormData(this);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let responseDiv = document.getElementById('response');
        let graphImg = document.getElementById('result-graph');
        let scoreDiv = document.getElementById('score');

        if (data.message) {
            responseDiv.innerHTML = `<p style="color:green;">${data.message}</p>`;
            graphImg.src = `data:image/png;base64,${data.plot_url}`;
            graphImg.style.display = "block";
            scoreDiv.textContent = `Resume Score: ${data.score}`;
        } else if (data.error) {
            responseDiv.innerHTML = `<p style="color:red;">${data.error}</p>`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
