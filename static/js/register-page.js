function get_email() {
  email = document.getElementById("email").value;
  localStorage.clear();
  localStorage.setItem("email", email);
}
