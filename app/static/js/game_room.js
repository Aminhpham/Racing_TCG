// Game Room Client
class GameRoomClient {
    constructor(matchId) {
        this.matchId = matchId;
        this.socket = io();
        this.selectedCard = null;
        this.gameState = null;
        this.cardDataCache = {};

        this.setupSocketListeners();
        this.setupUIHandlers();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.addLogMessage('Connected to game server');
            this.socket.emit('request_game_state');
        });

        this.socket.on('game_state_update', (data) => {
            const previousPhase = this.gameState?.phase;
            this.gameState = data;

            // Clear selected card when leaving strategy selection phase
            if (previousPhase === 'strategy_selection' && data.phase !== 'strategy_selection') {
                this.selectedCard = null;
            }

            this.updateUI();
        });

        this.socket.on('strategy_selected', (data) => {
            this.addLogMessage('Strategy card selected');
        });

        this.socket.on('strategy_reveal', (data) => {
            this.showStrategyReveal(data);
        });

        this.socket.on('tactic_played', (data) => {
            this.showTacticPlayed(data);
        });

        this.socket.on('player_passed', (data) => {
            this.addLogMessage('Player passed');
        });

        this.socket.on('speed_phase_results', (data) => {
            this.showSpeedResults(data);
        });

        this.socket.on('dice_roll_result', (data) => {
            this.showDiceRollResults(data);
        });

        this.socket.on('lap_completed', (data) => {
            this.showLapCompleted(data);
        });

        this.socket.on('game_over', (data) => {
            this.handleGameOver(data);
        });

        this.socket.on('player_disconnected', (data) => {
            this.addLogMessage(`${data.username} disconnected. Waiting ${data.timeout_seconds}s...`, 'warning');
        });

        this.socket.on('player_reconnected', (data) => {
            this.addLogMessage(`${data.username} reconnected!`, 'success');
        });

        this.socket.on('error', (data) => {
            this.showError(data.message);
        });
    }

    setupUIHandlers() {
        // Ready button
        const readyBtn = document.getElementById('ready-btn');
        if (readyBtn) {
            readyBtn.addEventListener('click', () => {
                this.socket.emit('ready_for_reveal');
                readyBtn.disabled = true;
            });
        }

        // Pass button
        const passBtn = document.getElementById('pass-btn');
        if (passBtn) {
            passBtn.addEventListener('click', () => {
                this.socket.emit('pass_react_phase');
            });
        }

        // Pit stop button
        const pitStopBtn = document.getElementById('pit-stop-btn');
        if (pitStopBtn) {
            pitStopBtn.addEventListener('click', () => {
                this.socket.emit('pit_stop', { pit_type: 'normal' });
            });
        }

        // Card click handlers (delegated)
        const handContainer = document.getElementById('hand-cards');
        if (handContainer) {
            handContainer.addEventListener('click', (e) => {
                const cardElement = e.target.closest('.card');
                if (cardElement) {
                    this.handleCardClick(cardElement);
                }
            });
        }
    }

    updateUI() {
        if (!this.gameState) return;

        const state = this.gameState;

        // Update phase indicator
        document.getElementById('phase-text').textContent = this.formatPhase(state.phase);
        document.getElementById('turn-number').textContent = state.turn;

        // Update leader indicator
        const leaderIndicator = document.getElementById('leader-indicator');
        if (state.is_leader) {
            leaderIndicator.textContent = '👑 Leading';
        } else {
            leaderIndicator.textContent = '📍 Trailing';
        }

        // Update player stats
        this.updateStats('player', state.your_state);
        this.updateStats('opp', state.opponent_state);

        // Update hand
        if (state.your_state.hand) {
            this.renderHand(state.your_state.hand);
        }

        // Update turn indicator and phase description
        this.updateTurnIndicator(state);
        this.updatePhaseDescription(state);

        // Show/hide action buttons based on phase
        this.updateActionButtons(state);
    }

    updateTurnIndicator(state) {
        const indicator = document.getElementById('turn-indicator');
        if (!indicator) return;

        if (state.phase === 'react') {
            if (state.can_act) {
                indicator.textContent = '🎯 Your Turn';
                indicator.className = 'turn-indicator your-turn';
            } else {
                indicator.textContent = '⏳ Opponent\'s Turn';
                indicator.className = 'turn-indicator opponent-turn';
            }
            indicator.style.display = 'block';
        } else {
            indicator.style.display = 'none';
        }
    }

    updatePhaseDescription(state) {
        const desc = document.getElementById('phase-description');
        if (!desc) return;

        const instructions = {
            'strategy_selection': this.selectedCard
                ? 'Click "Ready for Reveal" when you\'re ready'
                : 'Click a strategy card from your hand',
            'react': state.can_act
                ? 'Play a tactic card or click "Pass"'
                : 'Waiting for opponent to play or pass...',
            'speed_calculation': 'Calculating movement...',
            'game_over': state.winner_id ? 'Game Over!' : ''
        };

        desc.textContent = instructions[state.phase] || '';
    }

    updateStats(prefix, playerState) {
        // Update car stats
        document.getElementById(`${prefix}-engine`).textContent = playerState.car_stats.engine;
        document.getElementById(`${prefix}-tires`).textContent = playerState.car_stats.tires;
        document.getElementById(`${prefix}-fuel`).textContent = playerState.car_stats.fuel;
        document.getElementById(`${prefix}-reliability`).textContent = playerState.car_stats.reliability;
        document.getElementById(`${prefix}-speed`).textContent = playerState.current_speed || 0;

        // Update lap progress
        document.getElementById(`${prefix}-lap`).textContent = playerState.current_lap;
        document.getElementById(`${prefix}-progress`).textContent = playerState.lap_progress;

        // Update progress bar
        const progressPercent = (playerState.lap_progress / 10) * 100;
        document.getElementById(`${prefix}-progress-fill`).style.width = `${progressPercent}%`;

        if (prefix === 'player') {
            document.getElementById('player-resources').textContent = playerState.resources;
        } else {
            document.getElementById('opp-hand-count').textContent = playerState.hand_size;
        }
    }

    renderHand(cards) {
        const container = document.getElementById('hand-cards');
        container.innerHTML = '';

        // Handle both card objects and card IDs for backward compatibility
        cards.forEach(card => {
            let cardData, cardId;

            if (typeof card === 'object' && card !== null) {
                // New format: full card object
                cardData = card;
                cardId = card.id;
            } else {
                // Old format: just card ID
                cardId = card;
                cardData = this.getCardData(cardId);
            }

            const cardEl = CardRenderer.createCardElement(cardId, cardData);
            container.appendChild(cardEl);
        });
    }

    handleCardClick(cardElement) {
        const cardId = parseInt(cardElement.dataset.cardId);
        const phase = this.gameState.phase;

        if (phase === 'strategy_selection') {
            this.selectStrategyCard(cardId, cardElement);
        } else if (phase === 'react' && this.gameState.can_act) {
            this.playTacticCard(cardId);
        }
    }

    selectStrategyCard(cardId, cardElement) {
        // Highlight selected card
        CardRenderer.highlightCard(cardElement);

        this.selectedCard = cardId;
        this.socket.emit('select_strategy_card', { card_id: cardId });

        // Show ready button
        document.getElementById('ready-btn').style.display = 'block';
        document.getElementById('ready-btn').disabled = false;
    }

    playTacticCard(cardId) {
        this.socket.emit('play_tactic', { card_id: cardId, target: 'self' });
    }

    updateActionButtons(state) {
        const readyBtn = document.getElementById('ready-btn');
        const passBtn = document.getElementById('pass-btn');
        const pitStopBtn = document.getElementById('pit-stop-btn');

        readyBtn.style.display = 'none';
        passBtn.style.display = 'none';
        pitStopBtn.style.display = 'none';

        if (state.phase === 'strategy_selection' && this.selectedCard) {
            readyBtn.style.display = 'block';
        }

        if (state.phase === 'react') {
            passBtn.style.display = 'block';
            passBtn.disabled = !state.can_act;
        }

        // Show pit stop if lap progress is high
        if (state.your_state.lap_progress >= 8 && state.your_state.resources >= 2) {
            pitStopBtn.style.display = 'block';
        }
    }

    showStrategyReveal(data) {
        this.addLogMessage('Strategy cards revealed!', 'info');

        // Get current player's ID from game state
        const yourId = this.gameState?.your_state?.player_id;
        if (!yourId || !data[yourId]) return;

        const opponentId = Object.keys(data).find(id => parseInt(id) !== yourId);
        const yourData = data[yourId];
        const oppData = data[opponentId];

        // Populate the reveal overlay
        const overlay = document.getElementById('reveal-overlay');

        // Your card - use card.name (not card_name) and card.description
        const yourCardEl = document.getElementById('reveal-player-card');
        yourCardEl.innerHTML = `
            <div style="font-size: 20px; font-weight: bold; margin-bottom: 8px;">
                ${yourData.card?.name || yourData.changes?.card_name || 'Unknown'}
            </div>
            <div style="font-size: 14px; opacity: 0.9;">
                ${yourData.card?.description || yourData.changes?.description || ''}
            </div>
        `;

        // Your stat changes - use changes.stat_changes (not card.stat_changes)
        const yourChangesEl = document.getElementById('reveal-player-changes');
        yourChangesEl.innerHTML = this.formatStatChanges(yourData.changes?.stat_changes || {});

        // Opponent's card
        const oppCardEl = document.getElementById('reveal-opponent-card');
        oppCardEl.innerHTML = `
            <div style="font-size: 20px; font-weight: bold; margin-bottom: 8px;">
                ${oppData.card?.name || oppData.changes?.card_name || 'Unknown'}
            </div>
            <div style="font-size: 14px; opacity: 0.9;">
                ${oppData.card?.description || oppData.changes?.description || ''}
            </div>
        `;

        // Opponent's stat changes
        const oppChangesEl = document.getElementById('reveal-opponent-changes');
        oppChangesEl.innerHTML = this.formatStatChanges(oppData.changes?.stat_changes || {});

        // Show overlay and auto-close
        overlay.style.display = 'flex';
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 3500);
    }

    formatStatChanges(statChanges) {
        if (!statChanges || Object.keys(statChanges).length === 0) {
            return '<div style="margin-top: 8px; font-size: 14px;">No stat changes</div>';
        }

        const html = Object.entries(statChanges).map(([stat, value]) => {
            const sign = value > 0 ? '+' : '';
            const color = value > 0 ? '#4CAF50' : value < 0 ? '#f44336' : '#fff';
            return `<div style="margin-top: 4px; color: ${color};">
                ${stat}: ${sign}${value}
            </div>`;
        }).join('');

        return `<div style="margin-top: 12px; font-size: 14px;">${html}</div>`;
    }

    showTacticPlayed(data) {
        const effect = data.effect || {};
        const playerName = data.player_name || 'Player';

        // Enhanced log message with effect details
        const effectText = this.formatEffect(effect);
        this.addLogMessage(`${playerName} played ${effect.card_name}: ${effectText}`, 'info');
    }

    formatEffect(effect) {
        const parts = [];
        if (effect.stat_changes) {
            for (const [stat, value] of Object.entries(effect.stat_changes)) {
                const sign = value > 0 ? '+' : '';
                parts.push(`${sign}${value} ${stat}`);
            }
        }
        return parts.length > 0 ? parts.join(', ') : 'Special effect';
    }

    showSpeedResults(data) {
        const yourId = this.gameState.your_state.player_id;
        const yourResults = data[yourId];

        if (yourResults) {
            this.addLogMessage(
                `Speed Phase: Moved ${yourResults.total_movement} (Base: ${yourResults.base_speed}, Slipstream: ${yourResults.slipstream})`,
                'info'
            );

            if (yourResults.reliability_check && yourResults.reliability_check.required) {
                const check = yourResults.reliability_check;
                const result = check.success ? '✅ Passed' : '❌ Failed';
                this.addLogMessage(`Reliability Check: Roll ${check.roll} vs ${check.threshold} - ${result}`, check.success ? 'success' : 'danger');
            }
        }
    }

    showDiceRollResults(data) {
        const overlay = document.getElementById('dice-roll-overlay');
        const yourId = this.gameState?.your_state?.player_id;

        // Find opponent ID
        const opponentId = Object.keys(data).find(id => parseInt(id) !== yourId);

        // Populate your dice roll
        const yourData = data[yourId];
        if (yourData) {
            document.getElementById('player-roll').textContent = yourData.roll;
            document.getElementById('player-threshold').textContent = yourData.threshold;

            const resultEl = document.getElementById('player-dice-result');
            if (yourData.success) {
                resultEl.textContent = `✅ Success! Moving ${yourData.movement} spaces`;
                resultEl.className = 'dice-result success';
            } else {
                resultEl.textContent = '❌ Failed! No movement';
                resultEl.className = 'dice-result failure';
            }
        }

        // Populate opponent dice roll
        const oppData = data[opponentId];
        if (oppData) {
            document.getElementById('opp-roll').textContent = oppData.roll;
            document.getElementById('opp-threshold').textContent = oppData.threshold;

            const resultEl = document.getElementById('opp-dice-result');
            if (oppData.success) {
                resultEl.textContent = `✅ Success! Moving ${oppData.movement} spaces`;
                resultEl.className = 'dice-result success';
            } else {
                resultEl.textContent = '❌ Failed! No movement';
                resultEl.className = 'dice-result failure';
            }
        }

        // Show overlay
        overlay.style.display = 'flex';

        // Auto-hide after 4 seconds
        setTimeout(() => {
            overlay.style.display = 'none';
        }, 4000);
    }

    showLapCompleted(data) {
        this.addLogMessage(`Lap ${data.lap} completed!`, 'success');
    }

    handleGameOver(data) {
        const yourId = this.gameState.your_state.player_id;
        const won = data.winner_id === yourId;

        const modal = document.getElementById('game-over-modal');
        const title = document.getElementById('game-over-title');
        const message = document.getElementById('game-over-message');

        title.textContent = won ? '🏆 Victory!' : '😞 Defeat';
        message.textContent = won
            ? `You won by ${data.condition}!`
            : `You lost by ${data.condition}`;

        modal.style.display = 'flex';
    }

    addLogMessage(message, type = 'info') {
        const logDiv = document.getElementById('log-messages');
        const msgDiv = document.createElement('div');
        msgDiv.className = `log-entry log-${type}`;

        const time = new Date().toLocaleTimeString();
        msgDiv.textContent = `[${time}] ${message}`;

        logDiv.appendChild(msgDiv);
        logDiv.scrollTop = logDiv.scrollHeight;
    }

    showError(message) {
        this.addLogMessage(`Error: ${message}`, 'danger');
        alert(`Error: ${message}`);
    }

    formatPhase(phase) {
        const phaseNames = {
            'strategy_selection': 'Select Strategy Card',
            'strategy_reveal': 'Revealing Strategies',
            'react': 'React Phase - Play Tactics',
            'speed_calculation': 'Speed Calculation',
            'game_over': 'Game Over'
        };
        return phaseNames[phase] || phase;
    }

    getCardData(cardId) {
        // In production, fetch from API or cache
        if (this.cardDataCache[cardId]) {
            return this.cardDataCache[cardId];
        }

        // Placeholder data
        return {
            id: cardId,
            name: `Card ${cardId}`,
            card_type: 'strategy',
            stats: {}
        };
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    const matchId = parseInt(document.getElementById('game-container').dataset.matchId);
    new GameRoomClient(matchId);
});
