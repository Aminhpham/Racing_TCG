// Card Rendering Utilities
class CardRenderer {
    static createCardElement(cardId, cardData) {
        const div = document.createElement('div');
        div.className = 'card';
        div.dataset.cardId = cardId;

        // Card content
        div.innerHTML = `
            <div class="card-header">
                <span class="card-name">${cardData.name || `Card ${cardId}`}</span>
                <span class="card-type">${cardData.card_type || ''}</span>
            </div>
            <div class="card-body">
                ${this.formatCardStats(cardData.stats || {})}
            </div>
        `;

        return div;
    }

    static formatCardStats(stats) {
        const lines = [];

        if (stats.speed_modifier) {
            lines.push(`<div class="stat-line">Speed: +${stats.speed_modifier}</div>`);
        }

        if (stats.engine_wear) {
            lines.push(`<div class="stat-line warn">Engine Wear: ${stats.engine_wear}</div>`);
        }

        if (stats.effect_type) {
            lines.push(`<div class="stat-line">${stats.effect_type}</div>`);
        }

        // Add other stat modifications
        ['engine', 'tires', 'fuel', 'reliability'].forEach(stat => {
            if (stats[stat]) {
                const sign = stats[stat] > 0 ? '+' : '';
                lines.push(`<div class="stat-line">${stat}: ${sign}${stats[stat]}</div>`);
            }
        });

        return lines.join('') || '<div class="stat-line">No stats</div>';
    }

    static highlightCard(cardElement) {
        // Remove highlight from all cards
        document.querySelectorAll('.card').forEach(el => el.classList.remove('selected'));

        // Add highlight to selected card
        cardElement.classList.add('selected');
    }
}
