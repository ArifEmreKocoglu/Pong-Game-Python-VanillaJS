
// function createHomePage() {
//     var contentDiv = document.getElementById('content');
//     contentDiv.innerHTML = `
//         <h2>Hoş Geldiniz</h2>
//         <p>Bu ana sayfanızdır.</p>
//     `;
// }


// document.addEventListener('DOMContentLoaded', function () {
//     // Başlangıçta giriş sayfasını göster
//     // showLoginPage();

//     // Giriş butonuna tıklanınca giriş sayfasını göster
//     document.getElementById('loginButton').addEventListener('click', function () {
//         showLoginPage();
//     });

//     // Üye Ol butonuna tıklanınca üyelik sayfasını göster
//     document.getElementById('registerButton').addEventListener('click', function () {
//         showRegisterPage();
//     });
// });

function showLoginPage() {
    // var contentDiv = document.getElementById('content');
    // contentDiv.innerHTML = `
    //     <h2>Giriş Yap</h2>
    //     <form id="loginForm">
    //         <input type="text" id="loginUsername" placeholder="Kullanıcı Adı">
    //         <input type="password" id="loginPassword" placeholder="Şifre">
    //         <button type="submit" class="btn btn-primary">Giriş Yap</button>
    //     </form>
    //     <p>Üye değil misiniz? <button id="registerButton" class="btn btn-link">Üye Ol</button></p>
    // `;

    // Giriş formunu işle
    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();
        var username = document.getElementById('loginUsername').value;
        var password = document.getElementById('loginPassword').value;

        // Django backend'e giriş isteği gönder
        fetch('http://localhost:8000/api/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3000' // İzin verilen köken (origin)
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(function (response) {
            console.log(response);
            if (response.ok) {
                // Giriş başarılı ise burada işlem yapabilirsiniz
                return response.json();
                
            } else {
                throw new Error('Giriş Hatası');
            }
        })
        .then(function (data) {
            createHomePage();
            console.log('Giriş Başarılı', data);
        })
        .catch(function (error) {
            // Hata durumunda burada işlem yapabilirsiniz
            console.error('Giriş Hatası', error);
        });
    });
}

function showRegisterPage() {
    // var contentDiv = document.getElementById('content');
    // contentDiv.innerHTML = `
    //     <h2>Üye Ol</h2>
    //     <form id="registerForm">
    //         <input type="text" id="registerUsername" placeholder="Kullanıcı Adı">
    //         <input type="password" id="registerPassword" placeholder="Şifre">
    //         <button type="submit" class="btn btn-primary">Üye Ol</button>
    //     </form>
    //     <p>Zaten üye misiniz? <button id="loginButton" class="btn btn-link">Giriş Yap</button></p>
    // `;

    // Üyelik formunu işle
    document.getElementById('registerForm').addEventListener('submit', function (e) {
        e.preventDefault();
        var username = document.getElementById('registerUsername').value;
        var password = document.getElementById('registerPassword').value;

        // Django backend'e üyelik isteği gönder
        fetch('http://localhost:8000/api/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Origin': 'http://localhost:3000' // İzin verilen köken (origin)
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(function (response) {
            if (response.ok) {
                // Üyelik başarılı ise burada işlem yapabilirsiniz
                return response.json();
            } else {
                throw new Error('Üyelik Hatası');
            }
        })
        .then(function (data) {
            console.log('Üyelik Başarılı', data);
        })
        .catch(function (error) {
            // Hata durumunda burada işlem yapabilirsiniz
            console.error('Üyelik Hatası', error);
        });
    });
}
