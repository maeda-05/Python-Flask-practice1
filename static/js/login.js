const form = document.getElementById("login-form");

const cancelSubmit = () => {
  const username = form.username.value;
  const password = form.password.value;
  
  if (!username || !password) {
    alert("名前かパスワードを入力してください");
    return false;
  }
}
