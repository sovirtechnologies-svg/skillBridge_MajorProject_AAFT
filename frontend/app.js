const authScreen = document.getElementById('auth-screen');
const appScreen = document.getElementById('app-screen');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');

document.getElementById('show-signup').addEventListener('click', (e) => { e.preventDefault(); loginForm.classList.add('hidden'); signupForm.classList.remove('hidden'); });
document.getElementById('show-login').addEventListener('click', (e) => { e.preventDefault(); signupForm.classList.add('hidden'); loginForm.classList.remove('hidden'); });

loginForm.addEventListener('submit', (e) => { e.preventDefault(); handleAuth(document.getElementById('login-email').value, "User"); });
signupForm.addEventListener('submit', (e) => { e.preventDefault(); handleAuth(document.getElementById('signup-email').value, document.getElementById('signup-name').value); });

function handleAuth(email, name) {
    localStorage.setItem('skillbridge_user', JSON.stringify({ email, name }));
    loadApp();
}

function handleLogout() {
    localStorage.removeItem('skillbridge_user');
    location.reload();
}

// --- TAB LOGIC ---
const TABS = ['home', 'jobs', 'learning'];

function switchTab(tabName, loadData = true) {
    if (!TABS.includes(tabName)) return;

    // 1. Hide all views
    TABS.forEach(t => {
        document.getElementById(`view-${t}`).classList.add('hidden');
    });

    // 2. Show target view
    document.getElementById(`view-${tabName}`).classList.remove('hidden');

    // 3. Update Nav State (Desktop & Mobile)
    document.querySelectorAll('.nav-item, .nav-item-mobile').forEach(el => {
        if (el.dataset.target === tabName) {
            el.classList.add('active', 'text-cyan-600');
            el.classList.remove('text-slate-400'); // For mobile
        } else {
            el.classList.remove('active', 'text-cyan-600');
            el.classList.add('text-slate-400'); // For mobile reset
        }
    });

    // 4. Lazy Load Data
    if (!loadData) return; // Skip loading if requested (e.g. when searching)

    if (tabName === 'home') {
        const postsContainer = document.getElementById('posts-container');
        if (!postsContainer.hasChildNodes() || postsContainer.querySelector('.fa-spin')) {
            fetchPosts();
        }
    } else if (tabName === 'jobs') {
        const jobsContainer = document.getElementById('job-feed-container');
        // Check if empty or has loader (this is a simple check)
        if (!jobsContainer.hasChildNodes() || jobsContainer.innerHTML.includes('Loading')) {
            fetchJobs();
        }
    }
}

// --- APP LOGIC ---
const API_URL = "http://127.0.0.1:5000/api";

function loadApp() {
    const user = JSON.parse(localStorage.getItem('skillbridge_user'));
    if (user) {
        authScreen.classList.add('hidden');
        appScreen.classList.remove('hidden');
        document.getElementById('display-name').innerText = user.name;
        document.getElementById('user-avatar').src = `https://ui-avatars.com/api/?name=${user.name}&background=06b6d4&color=fff&bold=true`;
        document.getElementById('current-user-avatar').src = `https://ui-avatars.com/api/?name=${user.name}&background=06b6d4&color=fff&bold=true`;

        // DEFAULT TAB
        switchTab('home');

    } else {
        authScreen.classList.remove('hidden');
        appScreen.classList.add('hidden');
    }
}

// --- NEW: POSTS LOGIC ---
// --- NEW: POSTS LOGIC ---
async function fetchPosts() {
    const container = document.getElementById('posts-container');
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout

    try {
        const res = await fetch(`${API_URL}/posts`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (!res.ok) throw new Error("Server error");

        const posts = await res.json();
        renderPosts(posts);
    } catch (error) {
        console.error("Error fetching posts:", error);
        container.innerHTML = `
            <div class="text-center py-10">
                <i class="fa-solid fa-triangle-exclamation text-red-500 text-3xl mb-3"></i>
                <p class="text-slate-600 font-bold">Failed to connect to server</p>
                <p class="text-xs text-slate-400 mt-1">Is the backend running?</p>
                <button onclick="fetchPosts()" class="mt-4 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm font-bold text-slate-700 transition">
                    Retry
                </button>
            </div>
        `;
    }
}

function renderPosts(posts) {
    const container = document.getElementById('posts-container');
    container.innerHTML = '';

    if (posts.length === 0) {
        container.innerHTML = '<div class="text-center text-slate-500 py-10">No posts yet. Be the first to share!</div>';
        return;
    }

    posts.forEach(post => {
        const isAuthor = post.author === "Current User"; // Simple check for prototype

        const deleteButton = isAuthor ? `
            <button onclick="deletePost('${post.id}')" class="text-red-400 hover:text-red-600 transition p-2 hover:bg-red-50 rounded-full" title="Delete Post">
                <i class="fa-solid fa-trash"></i>
            </button>
        ` : `
            <button class="text-slate-400 hover:text-slate-600 transition p-2 hover:bg-slate-100 rounded-full">
                <i class="fa-solid fa-bookmark"></i>
            </button>
        `;

        const imageHtml = post.image ? `
            <div class="h-64 overflow-hidden">
                <img src="${post.image}" alt="Post Image" class="w-full h-full object-cover transition-transform duration-500 hover:scale-110">
            </div>
        ` : '';

        const html = `
            <article class="glass rounded-2xl overflow-hidden shadow-xl hover-lift animate-fade-in-up">
                <div class="p-6 border-b border-slate-200">
                    <div class="flex items-center justify-between mb-4">
                        <div class="flex items-center gap-4">
                            <img src="${post.avatar}" alt="${post.author}" class="w-12 h-12 rounded-full border-2 border-cyan-500">
                            <div>
                                <h3 class="font-bold text-slate-900">${post.author}</h3>
                                <p class="text-xs text-slate-500">${post.role} • ${post.time}</p>
                            </div>
                        </div>
                        ${deleteButton}
                    </div>
                    <p class="text-slate-700 leading-relaxed mb-4 whitespace-pre-line">${post.content}</p>
                </div>
                ${imageHtml}
                <div class="p-5 flex items-center justify-between border-t border-slate-200">
                    <div class="flex gap-6">
                        <button class="flex items-center gap-2 text-slate-600 hover:text-cyan-600 transition-all group">
                            <i class="fa-solid fa-thumbs-up group-hover:scale-110 transition-transform"></i>
                            <span class="text-sm font-semibold">${post.likes}</span>
                        </button>
                        <button class="flex items-center gap-2 text-slate-600 hover:text-blue-600 transition-all group">
                            <i class="fa-solid fa-comment group-hover:scale-110 transition-transform"></i>
                            <span class="text-sm font-semibold">${post.comments}</span>
                        </button>
                        <button class="flex items-center gap-2 text-slate-600 hover:text-emerald-600 transition-all group">
                            <i class="fa-solid fa-share group-hover:scale-110 transition-transform"></i>
                            <span class="text-sm font-semibold">${post.shares}</span>
                        </button>
                    </div>
                </div>
            </article>
        `;
        container.innerHTML += html;
    });
}

async function createPost() {
    const input = document.getElementById('post-content');
    const content = input.value.trim();
    if (!content) return alert("Post content cannot be empty!");

    try {
        const res = await fetch(`${API_URL}/posts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });

        if (res.ok) {
            input.value = ""; // Clear input
            fetchPosts(); // Reload feed
        }
    } catch (error) {
        console.error("Error creating post:", error);
        alert("Failed to create post");
    }
}

async function deletePost(id) {
    if (!confirm("Are you sure you want to delete this post?")) return;

    try {
        const res = await fetch(`${API_URL}/posts/${id}`, { method: 'DELETE' });
        if (res.ok) {
            fetchPosts(); // Reload feed
        }
    } catch (error) {
        console.error("Error deleting post:", error);
        alert("Failed to delete post");
    }
}


// --- NEW: SKILL SEARCH ---
function searchBySkills() {
    const skills = document.getElementById('skills-input').value;
    if (!skills) return alert("Please enter some skills!");

    // Update UI status
    document.getElementById('feed-status').innerText = `Matches for skills: "${skills}"`;
    searchJobs(skills);
}

// --- NEW: KEYWORD SEARCH ---
const searchBtn = document.getElementById('job-keyword-btn');
const searchInput = document.getElementById('job-keyword-search');

if (searchBtn) {
    searchBtn.addEventListener('click', () => {
        const query = searchInput.value;
        if (query) {
            document.getElementById('feed-status').innerText = `Results for "${query}"`;
            searchJobs(query);
        }
    });
}

if (searchInput) {
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value;
            if (query) {
                document.getElementById('feed-status').innerText = `Results for "${query}"`;
                searchJobs(query);
            }
        }
    });
}

// --- API INTERACTION ---
async function searchJobs(query) {
    const container = document.getElementById('job-feed-container');
    container.innerHTML = '<div class="p-8 text-center text-gray-500"><i class="fa-solid fa-circle-notch fa-spin text-2xl mb-2 text-brand"></i><p>AI is finding the best matches...</p></div>';

    try {
        const res = await fetch(`${API_URL}/recommend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, type: 'job' })
        });
        const data = await res.json();
        renderJobs(data.results);
    } catch (error) {
        console.error("Search Error:", error);
        container.innerHTML = '<div class="p-4 text-center text-red-500">Connection Error</div>';
    }
}

async function fetchJobs() {
    const container = document.getElementById('job-feed-container');
    container.innerHTML = '<div class="p-4 text-center text-gray-500">Loading jobs...</div>';
    try {
        const res = await fetch(`${API_URL}/jobs`);
        const jobs = await res.json();
        renderJobs(jobs);
        document.getElementById('feed-status').innerText = "Based on your profile";
    } catch (error) {
        console.error(error);
    }
}

function renderJobs(jobs) {
    const container = document.getElementById('job-feed-container');
    container.innerHTML = "";
    if (jobs.length === 0) {
        container.innerHTML = '<div class="p-8 text-center text-gray-500">No matches found. Try different skills.</div>';
        return;
    }

    jobs.forEach(job => {
        const card = document.createElement('div');
        card.className = "flex gap-4 p-4 border-b border-gray-200 hover:bg-blue-50 transition cursor-pointer last:border-none group";

        const matchBadge = job.match_score
            ? `<span class="ml-auto text-[10px] font-bold text-brand bg-blue-100 px-2 py-1 rounded-full border border-blue-200">🔥 ${job.match_score}% Match</span>`
            : '';

        card.innerHTML = `
            <div class="w-12 h-12 shrink-0 rounded flex items-center justify-center font-bold text-sm text-white shadow-sm ${job.company.includes('AI') ? 'bg-brand' : 'bg-gray-700'}">
                ${job.logo}
            </div>
            <div class="flex-grow">
                <div class="flex justify-between items-start">
                    <h4 class="text-brand font-bold text-base leading-tight mb-1 group-hover:underline">${job.title}</h4>
                    ${matchBadge}
                </div>
                <div class="text-sm text-gray-900 font-medium mb-1">${job.company}</div>
                <div class="text-xs text-gray-500 mb-2"><i class="fa-solid fa-location-dot mr-1"></i> ${job.location}</div>
                <div class="flex items-center text-xs text-gray-400 gap-3">
                    <span><i class="fa-regular fa-clock"></i> ${job.posted}</span>
                    <span class="text-green-600 font-bold">12 applicants</span>
                </div>
            </div>
            <div class="flex items-center pl-2">
                 <button class="border border-brand text-brand rounded-full px-4 py-1 font-bold text-xs hover:bg-brand hover:text-white transition">
                    Apply
                 </button>
            </div>
        `;
        container.appendChild(card);
    });
}

// --- REAL RESUME UPLOAD ---
async function handleResumeUpload(event) {
    console.log("DEBUG: handleResumeUpload triggered");

    // safe check for the input element
    const fileInput = event.target || document.getElementById('resume-upload');
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        console.warn("DEBUG: No file selected or input not found");
        return;
    }

    const file = fileInput.files[0];
    console.log("DEBUG: File selected:", file.name, file.type, file.size);

    const skillsArea = document.getElementById('skills-result-area');
    const skillsContainer = document.getElementById('extracted-skills-container');
    const progressBar = document.getElementById('scan-progress');
    const feedStatus = document.getElementById('feed-status');

    // 1. UI State: Show Progress, Hide previous skills
    if (progressBar) progressBar.classList.remove('hidden');
    if (skillsArea) skillsArea.classList.add('hidden');
    if (feedStatus) feedStatus.innerText = "Uploading & Analyzing...";

    const formData = new FormData();
    formData.append('resume', file);

    try {
        console.log("DEBUG: Sending request to", `${API_URL}/upload-resume`);
        // 2. Send to Backend
        const res = await fetch(`${API_URL}/upload-resume`, {
            method: 'POST',
            body: formData
        });

        console.log("DEBUG: Response status:", res.status);

        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(`Server returned ${res.status}: ${errorText}`);
        }

        const data = await res.json();
        console.log("DEBUG: Response data received:", data);

        if (progressBar) progressBar.classList.add('hidden');

        if (data.error) {
            throw new Error(data.error);
        }

        // 3. RENDER SKILLS
        if (skillsContainer) {
            if (data.extracted_skills && data.extracted_skills.length > 0) {
                skillsContainer.innerHTML = data.extracted_skills.map(skill => `
                    <span class="px-3 py-1 bg-purple-50 text-purple-700 border border-purple-200 rounded-full text-xs font-semibold shadow-sm">
                        ${skill}
                    </span>
                `).join('');

                // Populate manual search box
                const skillsInput = document.getElementById('skills-input');
                if (skillsInput) skillsInput.value = data.extracted_skills.join(', ');
            } else {
                skillsContainer.innerHTML = '<span class="text-xs text-gray-500">No specific skills detected, but we matched based on context!</span>';
            }
        }

        if (skillsArea) skillsArea.classList.remove('hidden');

        // 4. Render Jobs
        if (feedStatus) feedStatus.innerText = `Matches based on ${file.name}`;
        renderJobs(data.results);

        // Clear input so same file can be uploaded again if needed
        fileInput.value = '';

    } catch (error) {
        console.error("Upload Error:", error);
        if (progressBar) progressBar.classList.add('hidden');
        if (feedStatus) feedStatus.innerText = "Upload Failed";
        alert(`Failed to upload resume: ${error.message}\n\nPlease check console for details.`);
    }
}

// Ensure the listener is attached even if the element is dynamically loaded or switched
function attachResumeListener() {
    const resumeInput = document.getElementById('resume-upload');
    if (resumeInput) {
        // Remove old listener to avoid duplicates if this is called multiple times
        resumeInput.removeEventListener('change', handleResumeUpload);
        resumeInput.addEventListener('change', handleResumeUpload);
        console.log("DEBUG: Resume upload listener attached");
    } else {
        console.warn("DEBUG: Resume upload input element not found yet");
    }
}

// Call it initially
attachResumeListener();

// Also call it when switching tabs, just in case the DOM is manipulated/re-rendered
// (Adding this hook to the existing switchTab function locally or just relying on it being static in index.html)
// For now, since index.html structure seems static for the upload button, just calling it here is good.
// But let's export it or make it global if needed.

console.log("DEBUG: App.js loaded and listeners attached");