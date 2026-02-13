// Lobby Browser Client
class LobbyBrowserClient {
    constructor() {
        this.socket = io();
        this.selectedDeck = null;
        this.pendingLobbyId = null;

        this.setupSocketListeners();
        this.setupUIHandlers();
        this.requestLobbyList();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.requestLobbyList();
        });

        this.socket.on('lobby_created', (data) => {
            console.log('Lobby created:', data);
            this.requestLobbyList();
        });

        this.socket.on('lobby_list_update', (data) => {
            this.updateLobbyList(data.lobbies);
        });

        this.socket.on('game_starting', (data) => {
            console.log('Game starting:', data);
            // Redirect to game room
            window.location.href = `/matchmaking/game/${data.match_id}`;
        });

        this.socket.on('error', (data) => {
            alert('Error: ' + data.message);
        });
    }

    setupUIHandlers() {
        // Deck selector
        const deckSelector = document.getElementById('deck-selector');
        const createBtn = document.getElementById('create-lobby-btn');

        if (deckSelector) {
            deckSelector.addEventListener('change', (e) => {
                this.selectedDeck = e.target.value ? parseInt(e.target.value) : null;
                createBtn.disabled = !this.selectedDeck;
            });
        }

        // Private checkbox
        const privateCheckbox = document.getElementById('is-private');
        const passwordGroup = document.getElementById('password-group');

        if (privateCheckbox) {
            privateCheckbox.addEventListener('change', (e) => {
                passwordGroup.style.display = e.target.checked ? 'block' : 'none';
            });
        }

        // Create lobby form
        const createForm = document.getElementById('create-lobby-form');
        if (createForm) {
            createForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.createLobby();
            });
        }

        // Password modal handlers
        const joinWithPasswordBtn = document.getElementById('join-with-password-btn');
        const cancelJoinBtn = document.getElementById('cancel-join-btn');

        if (joinWithPasswordBtn) {
            joinWithPasswordBtn.addEventListener('click', () => {
                this.joinLobbyWithPassword();
            });
        }

        if (cancelJoinBtn) {
            cancelJoinBtn.addEventListener('click', () => {
                this.hidePasswordModal();
            });
        }
    }

    createLobby() {
        if (!this.selectedDeck) {
            alert('Please select a deck first!');
            return;
        }

        const lobbyName = document.getElementById('lobby-name').value || 'My Game';
        const isPrivate = document.getElementById('is-private').checked;
        const password = isPrivate ? document.getElementById('lobby-password').value : null;

        this.socket.emit('create_lobby', {
            deck_id: this.selectedDeck,
            lobby_name: lobbyName,
            is_private: isPrivate,
            password: password
        });
    }

    joinLobby(lobbyId, isPrivate) {
        if (!this.selectedDeck) {
            alert('Please select a deck first!');
            return;
        }

        if (isPrivate) {
            this.pendingLobbyId = lobbyId;
            this.showPasswordModal();
        } else {
            this.socket.emit('join_lobby', {
                lobby_id: lobbyId,
                deck_id: this.selectedDeck
            });
        }
    }

    joinLobbyWithPassword() {
        const password = document.getElementById('join-password').value;

        this.socket.emit('join_lobby', {
            lobby_id: this.pendingLobbyId,
            deck_id: this.selectedDeck,
            password: password
        });

        this.hidePasswordModal();
    }

    showPasswordModal() {
        document.getElementById('password-modal').style.display = 'flex';
    }

    hidePasswordModal() {
        document.getElementById('password-modal').style.display = 'none';
        document.getElementById('join-password').value = '';
        this.pendingLobbyId = null;
    }

    requestLobbyList() {
        this.socket.emit('list_lobbies');
    }

    updateLobbyList(lobbies) {
        const listContainer = document.getElementById('lobby-list');

        if (lobbies.length === 0) {
            listContainer.innerHTML = '<p class="text-muted">No lobbies available. Create one!</p>';
            return;
        }

        listContainer.innerHTML = '';

        lobbies.forEach(lobby => {
            const lobbyCard = document.createElement('div');
            lobbyCard.className = 'lobby-card';
            lobbyCard.innerHTML = `
                <div class="lobby-info">
                    <h4>${lobby.name} ${lobby.is_private ? '🔒' : ''}</h4>
                    <p>Host: ${lobby.host.username}</p>
                </div>
                <button class="btn btn-primary join-lobby-btn" data-lobby-id="${lobby.id}" data-is-private="${lobby.is_private}">
                    Join
                </button>
            `;

            // Add click handler to join button
            const joinBtn = lobbyCard.querySelector('.join-lobby-btn');
            joinBtn.addEventListener('click', () => {
                this.joinLobby(lobby.id, lobby.is_private);
            });

            listContainer.appendChild(lobbyCard);
        });
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new LobbyBrowserClient();
});
