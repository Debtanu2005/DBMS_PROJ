document.addEventListener("DOMContentLoaded", () => {
  const role = localStorage.getItem("role");
  const link = document.getElementById("addBookLink");

  console.log("ROLE:",role);
  console.log("LINK:",link);

  if (role =="admin" && link) {
    link.style.display = "inline";
  }
});