// Function to match patterns in an array of text
function findPatterns(textArray, patterns) {
    return textArray.filter(text => patterns.some(pattern => pattern.test(text)));
  }
  
  // Example usage
  const patterns = [new RegExp('sweatshirts'), new RegExp('pants')]; 
  const matchedText = findPatterns(allPageText, patterns);


  // Function to extract text from all elements and add them to an array
function extractTextFromElements() {
    const allElements = document.querySelectorAll('*'); // Select all elements in the DOM
    const allText = [];
  
    allElements.forEach(el => {
      if (el.textContent.trim() !== '') { // Check if the element has non-empty text content
        allText.push(el.textContent.trim());
      }
    });
  
    return allText;
  }
  
  // Use the function to get all text
  const allPageText = extractTextFromElements();