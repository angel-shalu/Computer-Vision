document.addEventListener('DOMContentLoaded', () => {
    const player = document.getElementById('player');
    const target = document.getElementById('target');
    const scoreElement = document.getElementById('score');
    const highScoreElement = document.getElementById('high-score');
    const gestureDisplay = document.getElementById('gesture-display');
    
    let score = 0;
    let highScore = localStorage.getItem('highScore') || 0;
    highScoreElement.textContent = highScore;
    
    // Initialize player position
    let playerPos = {
        x: 50,
        y: 50
    };
    
    // Set initial player position
    updatePlayerPosition();
    
    // Place initial target
    placeTarget();
    
    function updatePlayerPosition() {
        player.style.left = `${playerPos.x}px`;
        player.style.top = `${playerPos.y}px`;
    }
    
    function placeTarget() {
        const gameBoard = document.querySelector('.game-board');
        const maxX = gameBoard.clientWidth - 20;
        const maxY = gameBoard.clientHeight - 20;
        
        const x = Math.floor(Math.random() * maxX);
        const y = Math.floor(Math.random() * maxY);
        
        target.style.left = `${x}px`;
        target.style.top = `${y}px`;
    }
    
    function checkCollision() {
        const playerRect = player.getBoundingClientRect();
        const targetRect = target.getBoundingClientRect();
        
        return !(playerRect.right < targetRect.left || 
                playerRect.left > targetRect.right || 
                playerRect.bottom < targetRect.top || 
                playerRect.top > targetRect.bottom);
    }
    
    function updateScore() {
        score++;
        scoreElement.textContent = score;
        
        if (score > highScore) {
            highScore = score;
            highScoreElement.textContent = highScore;
            localStorage.setItem('highScore', highScore);
        }
    }
    
    function movePlayer(gesture) {
        const gameBoard = document.querySelector('.game-board');
        const step = 20;
        const maxX = gameBoard.clientWidth - player.clientWidth;
        const maxY = gameBoard.clientHeight - player.clientHeight;
        
        switch (gesture) {
            case 'left':
                playerPos.x = Math.max(0, playerPos.x - step);
                break;
            case 'right':
                playerPos.x = Math.min(maxX, playerPos.x + step);
                break;
            case 'up':
                playerPos.y = Math.max(0, playerPos.y - step);
                break;
            case 'down':
                playerPos.y = Math.min(maxY, playerPos.y + step);
                break;
        }
        
        updatePlayerPosition();
        
        if (checkCollision()) {
            updateScore();
            placeTarget();
        }
    }
    
    // Poll for gestures
    setInterval(() => {
        fetch('/get_gesture')
            .then(response => response.json())
            .then(data => {
                if (data.gesture !== 'none') {
                    gestureDisplay.textContent = data.gesture.toUpperCase();
                    movePlayer(data.gesture);
                }
            })
            .catch(error => console.error('Error:', error));
    }, 100);
});