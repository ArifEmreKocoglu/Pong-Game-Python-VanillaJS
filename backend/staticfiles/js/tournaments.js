document.getElementById('createTournament').addEventListener('click', function() {
    console.log("saa");
    document.getElementById('tournamentFormContainer').style.display = 'flex';
});

window.onclick = function(event) {
    let modal = document.getElementById('tournamentFormContainer');
    if (event.target === modal) {
        modal.style.display = "none";
    }
}


document.getElementById('createTournamentForm').addEventListener('click', function() {
    
    initializeTournamentWebSocket();

    var tournamentName = document.getElementById('tournamentName').value;
    var nickname = document.getElementById('nickname').value;

    document.getElementById('tournamentFormContainer').style.display = 'none';

        setTimeout(() => { 
            if (tournamentSocket.readyState === WebSocket.OPEN) {
                tournamentSocket.send(JSON.stringify({
                    action: 'create_tournament',
                    name: tournamentName,
                    nickname: nickname
                }));
            }
        }, 1000);

        history.pushState(null, '', '/tournament-page');
        routePage('/tournament-page');
});



let tournamentSocket;

function initializeTournamentWebSocket() {
    const tournamentServerUrl = `wss://${window.location.hostname}:8000/ws/tournaments/`;
    tournamentSocket= new WebSocket(tournamentServerUrl);

    tournamentSocket.addEventListener('open', (event) => {
        console.log('Turnuva WebSocket bağlantısı açıldı.');
    });

    tournamentSocket.addEventListener('close', (event) => {
        console.log('Turnuva WebSocket bağlantısı kapandı.');
    });

    tournamentSocket.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        const action = data.action;
        console.log(action);
    });
}



function fetchTournaments() {
    fetch('https://${window.location.hostname}:8000/api/tournaments/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: 'include'

    }) 
        .then(response => response.json())
        .then(tournaments => {
            const tournamentsList = document.getElementById('tournamentsList');
            tournamentsList.innerHTML = ''; // Listeyi temizle
            tournaments.forEach(tournament => {
                const li = document.createElement('li');
                li.innerText = tournament.name;  // Turnuva adı

                // Turnuvaya Katıl butonu
                const joinButton = document.createElement('button');
                joinButton.innerText = 'Turnuvaya Katıl';
                joinButton.onclick = function() {
                    // Katılma işlemi (Örn: katılma isteği gönderme, katılma sayfasına yönlendirme)
                };
                li.appendChild(joinButton);
                tournamentsList.appendChild(li);
            });
        })
        .catch(error => console.error('Error fetching tournaments:', error));
}