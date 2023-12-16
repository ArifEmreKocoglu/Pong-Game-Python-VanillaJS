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



function initializeUserPage() {
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



let playerUsername = null;
let opponentUsername = null;
let myPaddle = null;

function initializeMultiGame() {
    const serverUrl = `wss://${window.location.hostname}:8000/ws/pong/`;
    const socket = new WebSocket(serverUrl);

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
        
            history.pushState(null, '', '/multi-game');
            routePage('/multi-game');
        
        }else if (action === 'score_update') {
            if (data.username === playerUsername) {
                playerScore = data.score;
            } else {
                opponentScore = data.score;
            }
        }
        else if (action === 'update_state') {
            if (!data.state || typeof data.state !== 'object') {
                console.error('Invalid or incomplete game state received:', data);
                return;
            }
            updateGameState(data.state);
        }
    });
    
    document.addEventListener('keydown', e => {
        let paddleMovement = null;
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            paddleMovement = e.key === 'ArrowUp' ? 'up' : 'down';
            socket.send(JSON.stringify({ action: "move_paddle", direction: paddleMovement, username: playerUsername }));
        }
    });
    
    
}


let ball, playerPaddleY, opponentPaddleY, playerScore, opponentScore;

function startPongGame() {
    const canvas = document.getElementById('pongCanvas');
    const ctx = canvas.getContext('2d');

    playerScore = 0, opponentScore = 0;
    const winningScore = 10;
    ball = { x: canvas.width / 2, y: canvas.height / 2, radius: 10 };
    let paddleHeight = 100, paddleWidth = 10;
    playerPaddleY = canvas.height / 2 - paddleHeight / 2;
    opponentPaddleY = canvas.height / 2 - paddleHeight / 2;
    
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
        if (myPaddle === 'left') {
            ctx.fillText(`${playerUsername}: ${playerScore}`, 100, 50); 
            ctx.fillText(`${opponentUsername}: ${opponentScore}`, canvas.width - 200, 50);
        } else {
            ctx.fillText(`${opponentUsername}: ${opponentScore}`, 100, 50);
            ctx.fillText(`${playerUsername}: ${playerScore}`, canvas.width - 200, 50);
        }
    }

    function checkForWinner() {
        if (playerScore >= winningScore || opponentScore >= winningScore) {
            const winner = playerScore >= winningScore ? 'Player' : 'Opponent';
            alert(`${winner} kazandı!`);
            socket.close();
            history.pushState(null, '', '/user-page');
        }
    }

    function gameLoop() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawPaddle(0, playerPaddleY);
        drawPaddle(canvas.width - paddleWidth, opponentPaddleY);
        drawBall();
        drawScore();
        checkForWinner();
        requestAnimationFrame(gameLoop);
    }

    gameLoop();
}

function updateGameState(state) {
    if (ball && playerPaddleY !== undefined && opponentPaddleY !== undefined) {
        ball.x = state.ball.x;
        ball.y = state.ball.y;

        playerPaddleY = state.player_paddle.y;
        opponentPaddleY = state.opponent_paddle.y;

        console.log("opponentPaddleY");
        console.log(opponentPaddleY);
        console.log("playerPaddleY");
        console.log(playerPaddleY);
        
        playerScore = state.player_score;
        opponentScore = state.opponent_score;
    }
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


