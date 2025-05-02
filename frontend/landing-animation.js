// Landing Animation for Dark Web Monitoring Crawler
document.addEventListener('DOMContentLoaded', () => {
    // Create landing animation overlay
    const overlay = document.createElement('div');
    overlay.className = 'landing-overlay';
    
    // Create animation content
    overlay.innerHTML = `
        <div class="hacker-animation">
            <div class="terminal">
                <div class="terminal-header">
                    <div class="terminal-buttons">
                        <span class="terminal-button close"></span>
                        <span class="terminal-button minimize"></span>
                        <span class="terminal-button maximize"></span>
                    </div>
                    <div class="terminal-title">secure_connection.sh</div>
                </div>
                <div class="terminal-content">
                    <div class="command-line">$ <span class="typing-text">initializing dark web crawler...</span></div>
                    <div class="command-output connecting">Establishing secure connection...</div>
                    <div class="command-output">Routing through encrypted nodes...</div>
                    <div class="command-output">Bypassing security protocols...</div>
                    <div class="command-output">Accessing dark web monitoring system...</div>
                    <div class="command-output success">Connection established. Welcome to the Dark Web Monitoring Crawler.</div>
                </div>
            </div>
            <div class="binary-rain"></div>
        </div>
        <div class="enter-button">
            <button id="enter-app">ENTER <i class="fas fa-arrow-right"></i></button>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    // Create binary rain effect
    const binaryRain = document.querySelector('.binary-rain');
    for (let i = 0; i < 50; i++) {
        const binaryStream = document.createElement('div');
        binaryStream.className = 'binary-stream';
        binaryStream.style.left = `${Math.random() * 100}%`;
        binaryStream.style.animationDuration = `${Math.random() * 3 + 2}s`;
        binaryStream.style.animationDelay = `${Math.random() * 2}s`;
        
        // Generate random binary content
        let binaryContent = '';
        for (let j = 0; j < 20; j++) {
            binaryContent += Math.random() > 0.5 ? '1' : '0';
            if (j % 4 === 3) binaryContent += '<br>';
        }
        binaryStream.innerHTML = binaryContent;
        
        binaryRain.appendChild(binaryStream);
    }
    
    // Typing animation for terminal text
    const typingText = document.querySelector('.typing-text');
    const text = typingText.textContent;
    typingText.textContent = '';
    
    let charIndex = 0;
    const typingInterval = setInterval(() => {
        if (charIndex < text.length) {
            typingText.textContent += text.charAt(charIndex);
            charIndex++;
        } else {
            clearInterval(typingInterval);
            // Show command outputs with delay
            const outputs = document.querySelectorAll('.command-output');
            outputs.forEach((output, index) => {
                setTimeout(() => {
                    output.classList.add('visible');
                    
                    // If it's the last output, show the enter button
                    if (index === outputs.length - 1) {
                        setTimeout(() => {
                            document.querySelector('.enter-button').classList.add('visible');
                        }, 500);
                    }
                }, 500 + (index * 700));
            });
        }
    }, 50);
    
    // Handle enter button click
    document.getElementById('enter-app').addEventListener('click', () => {
        overlay.classList.add('fade-out');
        setTimeout(() => {
            overlay.remove();
            // Trigger entrance animations for main content
            document.querySelectorAll('.dashboard-card').forEach((card, index) => {
                setTimeout(() => {
                    card.classList.add('animate-in');
                }, index * 150);
            });
        }, 1000);
    });
});