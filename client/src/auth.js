export function login(username, pass, cb) {
  if (localStorage.token) {
    if (cb) {
      cb({
        authenticated: true,
      });
    }
    return
  }

  getToken(username, pass, (res) => {
    if (res.authenticated) {
      localStorage.token = res.data.token;
      if (cb) cb(res);
    } else {
      if (cb) cb(res);
    }
  })
}

export function logout() {
  delete localStorage.token
}

export function loggedIn() {
  return !!localStorage.token;
}

export function getToken(username, password, cb) {
  const data = {
    username: username,
    password: password,
  };
  fetch('/api/v1/tokens/', {
    method: 'post',
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    },
    body: JSON.stringify(data)
  })
      .then(function (responseObj) {
        responseObj.json().then((data) => {
          if (responseObj.status === 200) {
            cb({
              authenticated: true,
              data: data
            })
          } else if (responseObj.status === 400) {
            cb({
              authenticated: false,
              data: data
            })
          }
        });
      })
      .catch(function (error) {
        console.log('Request failed', error);
      });
}
