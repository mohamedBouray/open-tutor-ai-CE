<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    const classId = $page.params.id;
    let selectedAI = "GPT-4";
    let showDropdown = false;
    const aiOptions = ["GPT-4", "GPT-3.5", "Claude 3", "Gemini Pro"];

    function goBack() {
        goto('/teacher/Classes');
    }
    function selectAI(option: any) {
        selectedAI = option;
        showDropdown = false;
    }
    let participationRate = 75;
    let missingSubmissions = 3;
</script>

<div class="container">
    <header class="main-header">
        <div class="header-left">
            <button class="back-btn" on:click={goBack}>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M19 12H5M12 19l-7-7 7-7"/>
                </svg> Back 
            </button>
            <h1 class="logo">Teacher</h1>
        </div>

        <div class="header-right">
            <div class="ai-dropdown-container">
                <button class="ai-selector" on:click={() => showDropdown = !showDropdown}>
                    <span>Current AI: {selectedAI}</span>
                    <svg class="arrow {showDropdown ? 'open' : ''}" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M6 9l6 6 6-6" />
                    </svg>
                </button>

                {#if showDropdown}
                    <ul class="dropdown-menu">
                    {#each aiOptions as option}
                        <li on:click={() => selectAI(option)}>{option}</li>
                    {/each}
                    </ul>
                {/if}
            </div>

            <div class="profile-icons">
                <div class="icon-circle gray"></div>
                <div class="icon-circle gray"></div>
                <div class="icon-circle blue"></div>
            </div>
        </div>
    </header>

    <main class="content">
        <aside class="sidebar-left">
            <section class="card">
                <h2>Class Overview</h2>
                <div class="status">
                    <span class="dot green"></span> 24 Active Students
                </div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {participationRate}%"></div>
                </div>
                <p class="sub-text">{participationRate}% Participation Rate</p>
            </section>

            <section class="card">
                <h2>AI Content Tools</h2>
                <button class="btn-outline">Generate Quiz</button>
                <button class="btn-outline">Create Lesson Plan</button>
                <button class="btn-outline">Generate Exercises</button>
            </section>

            <div class="notification-card">
                <h3>Notifications</h3>
                <p class="error-text">{missingSubmissions} Missing Submissions</p>
            </div>
        </aside>

        <section class="main-content">
            <div class="content-box">
                <textarea placeholder="Enter your prompt here..."></textarea>
            </div>

            <div class="content-box result-area">
                <h3>Generated Content</h3>
                <div class="empty-state"></div>
            </div>
        </section>

        <aside class="sidebar-right">
            <section class="card">
                <h3>AI Templates</h3>
                <button class="template-btn">Quiz Template</button>
                <button class="template-btn">Lesson Plan Template</button>
                <button class="template-btn">Exercise Template</button>
                <button class="template-btn">Custom Template</button>
            </section>
            <section class="card">
                <h3>Save & Export</h3>
                <button class="template-btn">Save to Library</button>
                <button class="template-btn">Export Content</button>
            </section>
        </aside>
    </main>
</div>

<style>
    .container{
        display: flex;
        flex-direction: column;
        margin: 10px;
    }

    /* Header */
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0 2rem;
        height: 64px;
        background: white;
        border-bottom: 1px solid #e5e7eb;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    .header-left{
        display: flex;
        align-items: center;
        gap: 4rem;
    }

    .back-btn {
        display: flex;
        align-items: center;
        gap: 8px;
        background: none;
        border: none;
        color: #64748b;
        font-weight: 600;
        cursor: pointer;
        padding: 10px 0;
        margin-bottom: 15px;
        transition: color 0.2s;
        margin: 0;
    }
    .back-btn:hover {
        color: #667eea; 
    }
    .back-btn svg {
        transition: transform 0.2s;
    }
    .back-btn:hover svg {
        transform: translateX(-5px); 
    }

    .logo {
        font-size: 1.25rem;
        font-weight: 500;
        color: #111827;
    }

    .header-right {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }

    .ai-dropdown-container {
        position: relative;
    }

    .ai-selector {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        background: #f9fafb;
        cursor: pointer;
        font-size: 14px;
        color: #374151;
        transition: border-color 0.2s;
    }

    .ai-selector:hover {
        border-color: #3b82f6;
    }

    .arrow {
        transition: transform 0.2s;
    }
    .arrow.open {
        transform: rotate(180deg);
    }

    .dropdown-menu {
        position: absolute;
        top: 110%;
        right: 0;
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        list-style: none;
        padding: 4px;
        width: 150px;
    }
    .dropdown-menu li {
        padding: 8px 12px;
        cursor: pointer;
        border-radius: 4px;
        font-size: 14px;
    }
    .dropdown-menu li:hover {
        background-color: #eff6ff;
        color: #1d4ed8;
    }

    .profile-icons {
        display: flex;
        gap: 10px;
    }

    .icon-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
    }
    .gray { background-color: #e5e7eb; }
    .blue { background-color: #3b82f6; }

    .content {
        display: grid;
        grid-template-columns: 250px 1fr 250px; 
        gap: 20px;
        padding: 20px;
        flex: 1;
    }

    /* Common Cards Style */
    .card, .notification-card, .content-box {
        background: #f8fbff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }

    h2 {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        color: #1a202c;
    }

    /* Left Sidebar Elements */
    .dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; }
    .green { background-color: #48bb78; }
    
    .progress-container {
        background: #edf2f7;
        height: 8px;
        border-radius: 4px;
        margin: 10px 0;
    }
    .progress-bar {
        background: #4299e1;
        height: 100%;
        border-radius: 4px;
    }

    .btn-outline {
        width: 100%;
        background: white;
        border: 1px solid #3b82f6;
        color: #3b82f6;
        padding: 8px;
        border-radius: 6px;
        margin-bottom: 8px;
        cursor: pointer;
        text-align: left;
    }

    .notification-card { background-color: #fff5f5; border-color: #feb2b2; }
    .error-text { color: #e53e3e; font-size: 13px; }

    /* Main Content Area */
    .main-content { display: flex; flex-direction: column; gap: 20px; }
    
    textarea {
        width: 100%;
        min-height: 150px;
        border: none;
        background: transparent;
        outline: none;
        resize: vertical;
        font-size: 14px;
    }

    .result-area { flex: 1; background: white; }

    /* Right Sidebar Elements */
    .template-btn {
        width: 100%;
        background: white;
        border: 1px solid #e2e8f0;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        text-align: left;
        font-size: 13px;
        cursor: pointer;
    }
</style>