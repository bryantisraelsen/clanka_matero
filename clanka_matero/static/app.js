// Clanka Matero Web UI JavaScript

class ClankaMateroApp {
    constructor() {
        this.statusElements = {
            currentTemp: document.getElementById('current-temp'),
            desiredTemp: document.getElementById('desired-temp'),
            heaterStatus: document.getElementById('heater-status'),
            waterLevelStatus: document.getElementById('water-level-status'),
            autoHeatStatus: document.getElementById('auto-heat-status'),
            dispenseTime: document.getElementById('dispense-time'),
            dispenseEnabled: document.getElementById('dispense-enabled-status'),
            dispensingStatus: document.getElementById('dispensing-status')

        };

        this.controlElements = {
            desiredTempInput: document.getElementById('desired-temp-input'),
            setTempBtn: document.getElementById('set-temp-btn'),
            dispenseTimeInput: document.getElementById('dispense-time-input'),
            setDispenseTimeBtn: document.getElementById('set-dispense-time-btn'),
            toggleAutoHeatBtn: document.getElementById('toggle-auto-heat'),
            dispenseBtn: document.getElementById('dispense-btn'),
            dispenseEnabled: document.getElementById('dispense-enabled')
        };

        this.themeToggle = document.getElementById('theme-toggle');
        this.currentTheme = localStorage.getItem('theme') || 'dark';

        this.init();
    }

    init() {
        this.setupTheme();
        this.setupEventListeners();
        this.startPolling();
        this.loadInitialData();
    }

    setupTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        this.updateThemeButton();
    }

    updateThemeButton() {
        this.themeToggle.textContent = this.currentTheme === 'light' ? '🌙' : '☀️';
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        this.updateThemeButton();
    }

    setupEventListeners() {
        // Theme toggle
        this.themeToggle.addEventListener('click', () => this.toggleTheme());

        // Temperature control
        this.controlElements.setTempBtn.addEventListener('click', () => this.setDesiredTemperature());

        // Dispense time control
        this.controlElements.setDispenseTimeBtn.addEventListener('click', () => this.setDispenseTime());

        // Auto heat toggle
        this.controlElements.toggleAutoHeatBtn.addEventListener('click', () => this.toggleAutoHeat());

        // Dispense action
        this.controlElements.dispenseBtn.addEventListener('click', () => this.dispense());

        // Toggle dispense enable/disable
        this.controlElements.dispenseEnabled.addEventListener('click', () => this.toggleDispense());

        // Enter key support for inputs
        this.controlElements.desiredTempInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.setDesiredTemperature();
        });

        this.controlElements.dispenseTimeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.setDispenseTime();
        });
    }

    async loadInitialData() {
        await this.updateStatus();
    }

    startPolling() {
        // Poll every 2 seconds
        setInterval(() => this.updateStatus(), 2000);
    }

    async updateStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            this.updateStatusDisplay(data);
        } catch (error) {
            console.error('Failed to update status:', error);
        }
    }

    updateStatusDisplay(data) {
        console.log(data);
        this.statusElements.currentTemp.textContent = `${data.current_temp_f}°F`;
        this.statusElements.desiredTemp.textContent = `${data.target_temp_f}°F`;
        this.statusElements.dispenseTime.textContent = `${data.dispense_time_sec}s`;

        this.updateStatusIndicator(this.statusElements.heaterStatus, data.heating);
        this.statusElements.waterLevelStatus.textContent = data.water_ok ? 'ok' : 'low';
        this.statusElements.waterLevelStatus.setAttribute('data-status', data.water_ok);
        this.updateStatusIndicator(this.statusElements.autoHeatStatus, data.auto_heat_running);
        // this.updateStatusIndicator(this.statusElements.dispenseEnabled, data.dispense_enabled);
        this.updateStatusIndicator(this.statusElements.dispensingStatus, data.dispensing);

        // Update control values
        // this.controlElements.desiredTempInput.value = data.desired_temperature;
        // this.controlElements.dispenseTimeInput.value = data.dispense_time;
        this.controlElements.toggleAutoHeatBtn.textContent = data.auto_heat_on ? 'ON' : 'OFF';
        this.controlElements.toggleAutoHeatBtn.setAttribute('data-active', data.auto_heat_on);

        this.controlElements.dispenseEnabled.textContent = data.dispense_enabled ? 'YES' : 'NO';
        this.controlElements.dispenseEnabled.setAttribute('data-status', data.dispense_enabled);
    }

    updateStatusIndicator(element, isActive) {
        element.textContent = isActive ? 'ON' : 'OFF';
        element.setAttribute('data-status', isActive);
    }

    async setDesiredTemperature() {
        const temp_f = parseFloat(this.controlElements.desiredTempInput.value);
        if (isNaN(temp_f) || temp_f < 70 || temp_f > 212) {
            alert('Please enter a valid temperature between 20°F and 212°F');
            return;
        }
        
        try {
            const response = await fetch('/api/set_temp', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ temp_f })
            });

            if (response.ok) {
                await this.updateStatus();
            } else {
                alert('Failed to set temperature');
            }
        } catch (error) {
            console.error('Failed to set temperature:', error);
            alert('Failed to set temperature');
        }
    }

    async setDispenseTime() {
        const seconds = parseFloat(this.controlElements.dispenseTimeInput.value);
        if (isNaN(seconds) || seconds < 1 || seconds > 300) {
            alert('Please enter a valid time between 1 and 300 seconds');
            return;
        }

        try {
            const response = await fetch('/api/set_dispense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ seconds })
            });

            if (response.ok) {
                await this.updateStatus();
            } else {
                alert('Failed to set dispense time');
            }
        } catch (error) {
            console.error('Failed to set dispense time:', error);
            alert('Failed to set dispense time');
        }
    }

    async toggleAutoHeat() {
        const currentState = this.controlElements.toggleAutoHeatBtn.getAttribute('data-active') === 'true';
        const newState = !currentState;
        let endpoint;
        try {
            if (newState) {
                endpoint = '/api/start_auto';
            } else {
                endpoint = '/api/stop_auto';
            }
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
                

            if (response.ok) {
                await this.updateStatus();
            } else {
                alert('Failed to toggle auto heat');
            }
        } catch (error) {
            console.error('Failed to toggle auto heat:', error);
            alert('Failed to toggle auto heat');
        }
    }

    async dispense() {
        try {
            const response = await fetch('/api/dispense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                const data = await response.json();
                alert(data.ok);
            } else {
                alert('Failed to dispense');
            }
        } catch (error) {
            console.error('Failed to dispense:', error);
            alert('Failed to dispense');
        }
    }

    async toggleDispense() {
        const currentState = this.statusElements.dispenseEnabled.getAttribute('data-status') === 'true';
        const newState = !currentState;
        let endpoint;
        if (newState) {
            endpoint = '/api/dispense_enable';
        } else {
            endpoint = '/api/dispense_disable';
        }
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (response.ok) {
                await this.updateStatus();
            } else {
                alert('Failed to toggle dispensability');
            }

        } catch (error) {
            console.error('Failed to toggle dispensability:', error);
            alert('Failed to toggle dispensability');
        }
    }

}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ClankaMateroApp();
});