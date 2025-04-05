document.addEventListener('DOMContentLoaded', function() {
  // Select all forms with class "upload-form"
  const forms = document.querySelectorAll('form.upload-form');
  
  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = new FormData(form);
      const resultBox = form.querySelector('.result-box');
      const loading = form.querySelector('.loading');
      const errorMsg = form.querySelector('.error-message');
      
      // Clear previous messages and show the loading spinner.
      errorMsg.textContent = '';
      resultBox.innerHTML = '';
      loading.style.display = 'block';
      
      try {
        const response = await fetch('/process', {
          method: 'POST',
          body: formData
        });
        
        const data = await response.json();
        
        if (!data.result) {
          throw new Error("No result returned from server.");
        }
        displayResults(data.result, resultBox);
      } catch (error) {
        errorMsg.textContent = error.message || 'An error occurred during processing';
      } finally {
        loading.style.display = 'none';
      }
    });
  });
});

function displayResults(result, resultBox) {
  if (typeof result === "string") {
    resultBox.innerHTML = result.replace(/\n/g, '<br>');
  } else if (Array.isArray(result)) {
    result.forEach(item => {
      const p = document.createElement('p');
      p.textContent = typeof item === 'object' ? JSON.stringify(item, null, 2) : item;
      resultBox.appendChild(p);
    });
  } else if (typeof result === "object") {
    resultBox.innerHTML = '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
  } else {
    resultBox.textContent = result;
  }
}
