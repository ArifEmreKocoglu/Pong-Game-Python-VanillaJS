let winner = null;
let playerUsername = null;
let opponentUsername = null;

let playerScore;
let opponentScore;
let matchCount = 0


document.addEventListener('DOMContentLoaded', function () {
    routePage(window.location.pathname); // İlk yüklemeyi ele al
});

function routePage(path) {

    fetchContent(path).then(html => {
        document.getElementById('content').innerHTML = html;
        
        if (path.endsWith('/login')) {
            initializeLoginForm();
        } else if (path.endsWith('/register')) {
            initializeRegisterForm();
        }else if(path.endsWith('/user-page')) 
        {
            initializeUserPage();
        }
        else if(path.endsWith('/game')) {
            initializePongGame();
        }
        else if(path.endsWith('/multi-game')) {
            startPongGame(); 
        }
        else if(path.endsWith('/match-history')) {
            matchHistory();
        }
    });
}


function fetchContent(url) {
    // const fullUrl = `https://127.0.0.1:8000${url}`;
    console.log(url);
    return fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .catch(error => console.error('Error:', error));
}


document.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') {
        e.preventDefault();
        const url = e.target.getAttribute('href');
        history.pushState(null, '', url);
        routePage(url);
    }
});

window.addEventListener('popstate', function () {
    routePage(window.location.pathname);
});


function matchHistory()
{
    document.getElementById('returnProfile').addEventListener('click', function() {
        history.pushState(null, '', '/user-page');
        routePage('/user-page');
    });

    fetch(`https://${window.location.hostname}:8000/api/match-history/`, { 
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        if (data.length > 0) {
            displayMatchHistory(data);
        } else {
            console.log('Henüz oynanmış bir oyun yok.');
        }
    })
    .catch(error => console.error('Error:', error));
}

function initializeUserPage() {

    document.getElementById('avatarFileInput').addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                document.getElementById('avatarImage').src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    document.getElementById('avatarUploadForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        fetch(`https://${window.location.hostname}:8000/api/upload-avatar/`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            // Yanıt olarak alınan URL'i doğrudan kullan
            document.getElementById('avatarImage').src = data.avatarUrl;
            console.log(document.getElementById('avatarImage').src);
        })
        .catch(error => console.error('Error:', error));
    });
    
    document.getElementById('showMatchHistory').addEventListener('click', function() { 

        history.pushState(null, '', '/match-history');
        routePage('/match-history');
    });
    document.getElementById('logoutButton').addEventListener('click', function() {
        fetch(`https://${window.location.hostname}:8000/api/logout/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        })
        .then(response => {
            if(response.ok) {
                history.pushState(null, '', '/');
                routePage('/');
            }
        })
        .catch(error => console.error('Error:', error));
    });

    document.getElementById('searchGameButton').addEventListener('click', function() {
        showLoadingIcon();
        initializeMultiGame();
    });
}

function displayMatchHistory(data) {
    const matchHistory = document.getElementById('match-history');
    matchHistory.innerHTML = ''; // Mevcut içeriği temizle
    data.forEach((match, index) => {
        const row = document.createElement('tr');
        // Sıra numarası
        const th = document.createElement('th');
        th.scope = 'row';
        th.textContent = (index + 1).toString();
        row.appendChild(th);

        // Maç tarihi
        const dateCell = document.createElement('td');
        dateCell.textContent = new Date(match.date_played).toLocaleDateString(); // Tarih formatlama
        row.appendChild(dateCell);

        // Oyuncu isimleri
        if (playerUsername === match.player1_username)
        {
            const playerCell = document.createElement('td');
            playerCell.textContent = match.player1_username;
            row.appendChild(playerCell);
    
            const opponentCell = document.createElement('td');
            opponentCell.textContent = match.player2_username;
            row.appendChild(opponentCell);
        }else{
            const opponentCell = document.createElement('td');
            opponentCell.textContent = match.player2_username;
            row.appendChild(opponentCell);

            const playerCell = document.createElement('td');
            playerCell.textContent = match.player1_username;
            row.appendChild(playerCell);
        }
        // Skor
        const scoreCell = document.createElement('td');
        console.log(match.score_player1);
        console.log(playerScore);
        if(match.score_player2 < match.score_player1)
        {
            scoreCell.textContent = `${match.score_player2} - ${match.score_player1}`;
        }else
        {
            scoreCell.textContent = `${match.score_player1} - ${match.score_player2}`;
        }
        row.appendChild(scoreCell);

        matchHistory.appendChild(row);
        console.log(matchHistory);
    });
}


// function updateMatchHistory() {
  
//     const matchHistory = document.getElementById('match-history');
//     console.log(matchCount);

    
//     // Yeni satır oluştur
//     const row = document.createElement('tr');

//     // Sıra numarası sütunu
//     const th = document.createElement('th');
//     th.scope = 'row';
//     th.textContent = (matchCount).toString();
//     row.appendChild(th);

//     // Oyuncu ismi sütunu
//     const playerCell = document.createElement('td');
//     playerCell.textContent = playerUsername;
//     row.appendChild(playerCell);

//     // Rakip ismi sütunu
//     const opponentCell = document.createElement('td');
//     opponentCell.textContent = opponentUsername;
//     row.appendChild(opponentCell);

//     // Skor sütunu
//     const scoreCell = document.createElement('td');
//     scoreCell.textContent = `${playerScore} - ${opponentScore}`;
//     row.appendChild(scoreCell);

//     // Satırı tabloya ekle
//     matchHistory.appendChild(row);

//     console.log(matchHistory);

//     matchCount++; // Sayacı arttır

//     // Skorları sıfırla veya güncelle
//     playerScore = 0;
//     opponentScore = 0;
// }


function initializeLoginForm() {
    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();
        var username = document.getElementById('loginUsername').value;
        var password = document.getElementById('loginPassword').value;

        fetch(`https://${window.location.hostname}:8000/api/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(function (response) {
            console.log(response);
            if (response.ok) {

                return response.json();
                
            } else {
                throw new Error('Giriş Hatası');
            }
        })
        .then(function (data) {
            console.log('Giriş Başarılı', data);
            history.pushState(null, '', '/user-page');
            routePage('/user-page'); 
        })
        .catch(function (error) {

            console.error('Giriş Hatası', error);
        });
    });
}

function initializeRegisterForm() {
    document.getElementById('registerForm').addEventListener('submit', function (e) {
        e.preventDefault();
        var username = document.getElementById('registerUsername').value;
        var password = document.getElementById('registerPassword').value;


        fetch(`https://${window.location.hostname}:8000/api/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                username: username,
                password: password
            })
        })
        .then(function (response) {
            if (response.ok) {

                return response.json();
            } else {
                throw new Error('Üyelik Hatası');
            }
        })
        .then(function (data) {
            console.log('Üyelik Başarılı', data);
            history.pushState(null, '', '/user-page');
            routePage('/user-page');
        })
        .catch(function (error) {

            console.error('Üyelik Hatası', error);
        });
    });
}



function initializePongGame() {
    const canvas = document.getElementById('pongCanvas');
    const ctx = canvas.getContext('2d');

    let playerScore = 0, aiScore = 0;
    const winningScore = 10;
    const paddleSpeed = 40;

    let ball = { x: canvas.width / 2, y: canvas.height / 2, radius: 10, speedX: 5, speedY: 5 };
    let paddleHeight = 100, paddleWidth = 10;
    let playerPaddleY = (canvas.height - paddleHeight) / 2, aiPaddleY = (canvas.height - paddleHeight) / 2;

    function drawPaddle(x, y) {
        ctx.fillStyle = 'white';
        ctx.fillRect(x, y, paddleWidth, paddleHeight);
    }
    function drawBall() {
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.closePath();
    }
    function drawScore() {
        ctx.fillStyle = 'white';
        ctx.font = '24px Arial';
        ctx.fillText(`Player: ${playerScore}`, 100, 50);
        ctx.fillText(`AI: ${aiScore}`, canvas.width - 150, 50);
    }

    function moveBall() {
        ball.x += ball.speedX;
        ball.y += ball.speedY;
    
        if (ball.y - ball.radius < 0 || ball.y + ball.radius > canvas.height) {
            ball.speedY = -ball.speedY;
        }
    
        if ((ball.x - ball.radius < paddleWidth && ball.y > playerPaddleY && ball.y < playerPaddleY + paddleHeight) ||
            (ball.x + ball.radius > canvas.width - paddleWidth && ball.y > aiPaddleY && ball.y < aiPaddleY + paddleHeight)) {
            ball.speedX = -ball.speedX;
        }
    
        if (ball.x - ball.radius < 0) {
            aiScore++;
            resetBall();
        } else if (ball.x + ball.radius > canvas.width) {
            playerScore++;
            resetBall();
        }
    
        checkScore();
    }

    function checkScore() {
        if (playerScore >= winningScore || aiScore >= winningScore) {
            let winner = playerScore >= winningScore ? 'Player' : 'AI';
            alert(`${winner} wins!`);
            playerScore = aiScore = 0; 
        }
    }

    function resetBall() {
        ball.x = canvas.width / 2;
        ball.y = canvas.height / 2;
        ball.speedX = 5;
        ball.speedY = 5;
    }

    function gameLoop() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawPaddle(0, playerPaddleY);
        drawPaddle(canvas.width - paddleWidth, aiPaddleY);
        drawBall();
        drawScore();
        moveBall();
        requestAnimationFrame(gameLoop);
    }

    document.addEventListener('keydown', e => {
        if (e.key === 'ArrowUp' && aiPaddleY > 0) aiPaddleY -= paddleSpeed;
        if (e.key === 'ArrowDown' && aiPaddleY < canvas.height - paddleHeight) aiPaddleY += paddleSpeed;
        if (e.key === 'w' && playerPaddleY > 0) playerPaddleY -= paddleSpeed;
        if (e.key === 's' && playerPaddleY < canvas.height - paddleHeight) playerPaddleY += paddleSpeed;
    });

    gameLoop();
}




let myPaddle = null;
let socket;
function initializeMultiGame() {
    const serverUrl = `wss://${window.location.hostname}:8000/ws/pong/`;
    socket = new WebSocket(serverUrl);

    socket.addEventListener('open', (event) => {
        console.log('WebSocket bağlantısı açıldı.');
    });

    socket.addEventListener('close', (event) => {
        console.log('WebSocket bağlantısı kapandı.');
    });

    socket.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        const action = data.action;
        if (action === 'matched') {
            console.log('Eşleşme bulundu:', data.message);
            myPaddle = data.paddle;
            playerUsername = data.username;
            opponentUsername = data.opponent_username;
            myPaddle = data.paddle;
            history.pushState(null, '', '/multi-game');
            routePage('/multi-game');
        
        }
        else if (action === 'update_ball'){

            updateBallPosition(data.state.ball);
        }else if (action === 'update_score'){

            updateScores({
                player_username: data.player_username,
                player_score: data.player_score,
                opponent_score: data.opponent_score
            });

        }
        else if (action === 'update_state') {
            
            if (!data.state || typeof data.state !== 'object') {
                console.error('Invalid or incomplete game state received:', data);
                return;
            }
            updatePaddlePositions(data.state);
        }
        else if(action === 'end_game')
        {
            console.log('Oyun bitti.');
            socket.close();
            socket.onclose = function(event) {
                console.log('WebSocket bağlantısı kapandı.');
                history.pushState(null, '', '/match-history');
                routePage('/match-history');

            };
        }
    });
    
    document.addEventListener('keydown', e => {
        let paddleMovement = null;
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            paddleMovement = e.key === 'ArrowUp' ? 'up' : 'down';
            console.log(playerUsername);
            socket.send(JSON.stringify({ action: "move_paddle", direction: paddleMovement, username: playerUsername }));
        }
    });
    
    
}

function updateBallPosition(ballData) {
    if (ball) {
        ball.x = ballData.x;
        ball.y = ballData.y;
    }
}

// updatePaddlePositions fonksiyonunu güncelleyin
function updatePaddlePositions(state) {
    if (myPaddle === 'right') {
        playerPaddleY = state.opponent_paddle.y;
        opponentPaddleY = state.player_paddle.y;
    } else {
        playerPaddleY = state.player_paddle.y;
        opponentPaddleY = state.opponent_paddle.y;
    }
}


let ball, playerPaddleY, opponentPaddleY;
let canvas;
let ctx;
function startPongGame() {
    canvas = document.getElementById('pongCanvas');
    ctx = canvas.getContext('2d');

    playerScore = 0, opponentScore = 0;
    const winningScore = 1;
    ball = { x: canvas.width / 2, y: canvas.height / 2, radius: 10 };
    let paddleHeight = 100, paddleWidth = 10;
    // playerPaddleY = canvas.height / 2 - paddleHeight / 2;
    // opponentPaddleY = canvas.height / 2 - paddleHeight / 2;
    
    function drawPaddle(x, y) {
        ctx.fillStyle = 'white';
        ctx.fillRect(x, y, paddleWidth, paddleHeight);
    }

    function drawBall() {
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.closePath();
    }


    // function checkForWinner() {
    //     if (playerScore >= winningScore || opponentScore >= winningScore) {
    //         winner = playerScore >= winningScore ? playerUsername : opponentUsername; // Kazanan oyuncunun kullanıcı adı
    
    //         socket.close();
    
    //         // WebSocket bağlantısı kapandıktan sonra çalışacak
    //         socket.onclose = function(event) {
    //             console.log('WebSocket bağlantısı kapandı.');
    //             history.pushState(null, '', '/match-history');
    //             routePage('/match-history');

    //         };
    //     }
    // }

    function gameLoop() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const playerPaddleX = myPaddle === 'right' ? canvas.width - paddleWidth : 0;
        const opponentPaddleX = myPaddle === 'right' ? 0 : canvas.width - paddleWidth;
        drawPaddle(playerPaddleX, playerPaddleY);
        drawPaddle(opponentPaddleX, opponentPaddleY);
        drawBall();
        drawScore();
        // checkForWinner();
        requestAnimationFrame(gameLoop);
    }

    gameLoop();
}

function updateScores(scoreData) {
    if (scoreData.player_username === playerUsername) {
        playerScore = scoreData.player_score;
        opponentScore = scoreData.opponent_score;
    } else {
        playerScore = scoreData.opponent_score;
        opponentScore = scoreData.player_score;
    }
    drawScore();
}

function drawScore() {
    ctx.fillStyle = 'white';
    ctx.font = '24px Arial';

    let leftUsername = myPaddle === 'left' ? playerUsername : opponentUsername;
    let rightUsername = myPaddle === 'left' ? opponentUsername : playerUsername;
    let leftScore = myPaddle === 'left' ?  opponentScore : playerScore;
    let rightScore = myPaddle === 'left' ? playerScore :opponentScore;

    ctx.fillText(`${leftUsername}: ${leftScore}`, 100, 50); 
    ctx.fillText(`${rightUsername}: ${rightScore}`, canvas.width - 200, 50);
}



function showLoadingIcon() {
    const loadingIcon = document.getElementById('loadingIcon') || document.createElement('div');
    loadingIcon.id = 'loadingIcon';
    loadingIcon.innerHTML = '<p>Arama yapılıyor...</p>';
    document.body.appendChild(loadingIcon);
}

function hideLoadingIcon() {
    const loadingIcon = document.getElementById('loadingIcon');
    if (loadingIcon) {
        loadingIcon.remove();
    }
}


