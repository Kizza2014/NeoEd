function displayResults(books) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = "";

    if (books.length === 0) {
        resultsDiv.innerHTML = "<p>No books found.</p>";
    } else {
        books.forEach(book => {
            const bookDiv = document.createElement('div');
            bookDiv.classList.add('book');
            bookDiv.innerHTML = `
                <img src="/thumbnail/${book._id}.jpg" alt="${book.title} thumbnail" class="book-thumbnail">
                <h3><a href="/books/${book._id}">${book.title}</a></h3>
                <p><strong>Published Year:</strong> ${book.published_year}</p>
                <p><strong>Authors:</strong> ${book.authors.join(', ')}</p>
            `;
            resultsDiv.appendChild(bookDiv);
        });
    }
}

