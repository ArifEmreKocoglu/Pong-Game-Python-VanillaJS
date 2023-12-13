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


document.getElementById('42Login').addEventListener('click', function() {
    console.log("saaa");
    fetch('https://127.0.0.1/8000/api/ft_api', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include'
    })
    .then(response => {
        if(response.ok) {

            return response.json();
        }else{
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


function fetchContent(url) {
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
        fetch('https://127.0.0.1:8000/api/logout/', {
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
        console.log("saa");
        showLoadingIcon();
        initializeMultiGame();
    });
}


function initializeLoginForm() {
    document.getElementById('loginForm').addEventListener('submit', function (e) {
        e.preventDefault();
        var username = document.getElementById('loginUsername').value;
        var password = document.getElementById('loginPassword').value;

        fetch('https://127.0.0.1:8000/api/login/', {
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


        fetch('https://127.0.0.1:8000/api/register/', {
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


function initializeMultiGame() {
    
        const serverUrl = 'wss://localhost:8000/ws/pong/';
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
                hideLoadingIcon();
 
                history.pushState(null, '', '/multi-game');
                routePage('/multi-game');
            } else if (action === 'update_state') {
                updateGameState(data.state);
            }
        });
    
        document.addEventListener('keydown', e => {

            let paddleMovement = null;
            if (e.key === 'ArrowUp') {
                paddleMovement = 'up';
            } else if (e.key === 'ArrowDown') {
                paddleMovement = 'down';
            }
    
            if (paddleMovement) {
                socket.send(JSON.stringify({ action: "move_paddle", direction: paddleMovement }));
            }
        });
    }

function startPongGame() {
    const canvas = document.getElementById('pongCanvas');
    const ctx = canvas.getContext('2d');
    let playerScore = 0, opponentScore = 0;
    const winningScore = 10;
    const paddleSpeed = 40;
    let ball = { x: canvas.width / 2, y: canvas.height / 2, radius: 10, speedX: 5, speedY: 5 };
    let paddleHeight = 100, paddleWidth = 10;
    let playerPaddleY = (canvas.height - paddleHeight) / 2, opponentPaddleY = (canvas.height - paddleHeight) / 2;

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
        ctx.fillText(`Opponent: ${opponentScore}`, canvas.width - 200, 50);
    }

    function checkForWinner(playerScore, aiScore) {
        if (playerScore >= 10 || aiScore >= 10) {

            const winner = playerScore >= 10 ? 'player' : 'ai';
            socket.send(JSON.stringify({ action: "game_over", winner: winner }));
            alert(winner + ' kazandı!');

            history.pushState(null, '', '/user-page');
            routePage('/user-page');
        }
    }

    function updateGameState(state) {

        ball.x = state.ball.x;
        ball.y = state.ball.y;
        playerPaddleY = state.playerPaddleY;
        opponentPaddleY = state.opponentPaddleY;
        playerScore = state.playerScore;
        opponentScore = state.opponentScore;
    }

    function gameLoop() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawPaddle(0, playerPaddleY);
        drawPaddle(canvas.width - paddleWidth, opponentPaddleY);
        drawBall();
        drawScore();
        

        updateGameState(gameState); 
        
        checkForWinner(playerScore, opponentScore);
        
        requestAnimationFrame(gameLoop);
    }
    let gameState = {};

    gameLoop();
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


