const BASE_URL = "/api";

// ADMIN CHECK
function checkAdmin() {
  const role = localStorage.getItem("role");

  if (role !== "admin") {
    alert("Access denied. Admins only.");
    window.location.href = "index.html";
  }
}
// SUBMIT FORM
document.getElementById("add-book-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const book = {
    title: document.getElementById("title").value,
    isbn: document.getElementById("isbn").value,
    publisher: document.getElementById("publisher").value,
    price: parseInt(document.getElementById("price").value),
    quantity: parseInt(document.getElementById("quantity").value),
    book_type: document.getElementById("book_type").value,
    purchase_option: document.getElementById("purchase_option").value,
    format: document.getElementById("format").value,
    language: document.getElementById("language").value,
    edition: parseInt(document.getElementById("edition").value),
    category: document.getElementById("category").value,
    course_id: parseInt(document.getElementById("course_id").value),
    type: document.getElementById("type").value
  };

  try {
    const token = localStorage.getItem("folio_token");

    const res = await fetch(`${BASE_URL}/add_book`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(book)
    });

    const data = await res.json();

    if (!res.ok) throw new Error(data.detail);

    document.getElementById("message").innerText = "✅ Book added successfully!";
    document.getElementById("add-book-form").reset();

  } catch (err) {
    document.getElementById("message").innerText = "❌ " + err.message;
  }
});

// RUN
window.onload = checkAdmin;