<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { fade, scale } from 'svelte/transition';
    import { browser } from '$app/environment';
    import { toast } from 'svelte-sonner';
    import QRCode from 'qrcode';
    import {addStudentToClass} from '$lib/apis/classe';

    const getToken = () => (browser ? localStorage.getItem('token') ?? '' : '');

    export let classId: string;
    $: inviteLink = `https://tutorClass.app/join/${classId}`;

    const dispatch = createEventDispatcher();
    
    // States
    let activeStep = 'selection';
    let copied = false;
    let studentName = '';
    let studentEmail = '';
    let isSubmitting = false;

    const methods = [
        {
            id: 'invite',
            title: 'Invite via Link or QR',
            desc: 'The fastest way. Students scan or click to join instantly.',
            icon: `<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/><line x1="7" y1="7" x2="7.01" y2="7"/><line x1="7" y1="17" x2="7.01" y2="17"/><line x1="17" y1="7" x2="17.01" y2="7"/>`,
            colorClass: 'text-blue-600 dark:text-blue-400',
            bgClass: 'bg-blue-50 dark:bg-blue-900/30',
            hoverBorder: 'hover:border-blue-500 dark:hover:border-blue-400'
        },
        {
            id: 'manual',
            title: 'Add manually',
            desc: 'Type names and create accounts one by one.',
            icon: `<path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="8.5" cy="7" r="4"/><line x1="20" y1="8" x2="20" y2="14"/><line x1="23" y1="11" x2="17" y2="11"/>`,
            colorClass: 'text-purple-600 dark:text-purple-400',
            bgClass: 'bg-purple-50 dark:bg-purple-900/30',
            hoverBorder: 'hover:border-purple-500 dark:hover:border-purple-400'
        }
    ];

    function selectMethod(id: string) { activeStep = id; }
    
    function goBack() { 
        activeStep = 'selection'; 
        studentName = '';
        studentEmail = '';
    }
// ===== Link ====
    async function copyLink() {
        try {
            await navigator.clipboard.writeText(inviteLink);
            copied = true;
            setTimeout(() => copied = false, 2000);
        } catch (err) { console.error('Err:', err); }
    }

// ===== QR Code ====
    function qrAction(node: HTMLCanvasElement, text: string) {
        const update = (newText: string) => {
            QRCode.toCanvas(node, newText, { width: 150, margin: 2, color: { dark: '#0f172a', light: '#ffffff' } });
        };
        update(text);
        return { update(newText: string) {
                update(newText);}};
    }

// ===== Add Manual ====
    async function handleManualAdd() {
        if (!studentEmail) return;
        isSubmitting = true;
        const token = getToken();
        try {
            const response = await addStudentToClass(token, {
                name: studentName,
                email: studentEmail,
                classId: classId
            });
            dispatch('save', response);
            studentName = '';
            studentEmail = '';
            toast.success("Student added successfully!"); 

        } catch (error) {
            toast.error("Error adding student "); 
        } finally {
            isSubmitting = false;
        }
    }
</script>

<div class="fixed inset-0 z-[1000] flex items-center justify-center bg-slate-900/70 dark:bg-black/80 p-5 backdrop-blur-sm">
    <div class="w-full max-w-[520px] rounded-[24px] bg-white dark:bg-gray-950 p-8 shadow-2xl overflow-hidden border border-transparent dark:border-gray-800" transition:scale={{ duration: 200, start: 0.95 }}>
        
        <header class="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-4 px-2">
            <div class="flex items-center gap-3">
                {#if activeStep !== 'selection' }
                    <button class="flex items-center gap-1.5 rounded-lg px-2 py-1 text-indigo-600 dark:text-indigo-400 transition-all hover:bg-gray-100 dark:hover:bg-gray-800 font-medium" on:click={goBack}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M19 12H5M12 19l-7-7 7-7"/>
                        </svg>
                        <span>Back</span>
                    </button>
                {/if}
                <h2 class="m-0 text-xl font-bold text-gray-900 dark:text-white">
                    {#if activeStep === 'selection'} Add Students 
                    {:else if activeStep === 'invite'} Invite Students
                    {:else if activeStep === 'manual'} Add Manually
                    {/if}
                </h2>
            </div>

            <button class="flex h-10 w-10 items-center justify-center rounded-lg text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white transition-all" on:click={() => dispatch('close')}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
            </button>
        </header>

        <div class="min-h-[300px] py-6">
            {#if activeStep === 'selection'}
                <div in:fade={{ duration: 250 }}>
                    <p class="mb-6 text-center text-[15px] text-gray-500 dark:text-gray-400">Choose how you'd like to add students to your class</p>
                    <div class="flex flex-col gap-3">
                        {#each methods as method}
                            <button 
                                class="group flex items-center border border-slate-100 dark:border-gray-800 bg-slate-50 dark:bg-gray-900/50 p-4 rounded-2xl transition-all hover:bg-white dark:hover:bg-gray-900 hover:translate-x-1 hover:shadow-md {method.hoverBorder}" 
                                on:click={() => selectMethod(method.id)}
                            >
                                <div class="mr-4 flex h-12 w-12 items-center justify-center rounded-xl {method.bgClass} {method.colorClass}">
                                    <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2">
                                        {@html method.icon}
                                    </svg>
                                </div>
                                <div class="flex-1 text-left">
                                    <h3 class="m-0 text-base font-semibold text-slate-800 dark:text-gray-200">{method.title}</h3>
                                    <p class="m-0 text-[13px] text-slate-500 dark:text-gray-400 leading-tight">{method.desc}</p>
                                </div>
                                <span class="text-xl opacity-20 dark:opacity-40 transition-opacity group-hover:opacity-100 dark:group-hover:text-white">→</span>
                            </button>
                        {/each}
                    </div>
                </div>

            {:else if activeStep === 'invite'}
                <div class="flex flex-col gap-6" in:fade={{ duration: 250 }}>
                    <div class="text-center">
                        <div class="mb-3 inline-flex rounded-2xl bg-white p-4 shadow-sm border dark:border-gray-800">
                            <canvas use:qrAction={inviteLink}></canvas>
                        </div>
                        <p class="text-sm text-gray-500 dark:text-gray-400">Scan QR Code to join</p>
                    </div>
                    <div class="flex items-center text-[10px] font-bold tracking-widest text-gray-300 dark:text-gray-600 uppercase before:flex-1 before:border-b before:border-gray-100 dark:before:border-gray-800 after:flex-1 after:border-b after:border-gray-100 dark:after:border-gray-800">
                        <span class="px-4">OR</span>
                    </div>
                    <div class="text-center">
                        <p class="mb-3 text-sm text-gray-500 dark:text-gray-400">Share this invitation link:</p>
                        <div class="flex flex-col sm:flex-row gap-2 rounded-xl border border-gray-200 dark:border-gray-800 bg-slate-50 dark:bg-gray-900 p-2">
                            <div class="flex flex-1 items-center gap-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 font-mono text-xs text-gray-700 dark:text-gray-300">
                                <span class="truncate">{inviteLink}</span>
                            </div>
                            <button 
                                class="flex items-center justify-center gap-1.5 rounded-lg px-4 py-2 text-sm font-semibold text-white transition-all active:scale-95 {copied ? 'bg-emerald-500' : 'bg-indigo-600 hover:bg-indigo-700'}" 
                                on:click={copyLink}>
                                {#if copied}
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 6L9 17l-5-5"/></svg>
                                    <span>Copied!</span>
                                {:else}
                                    <span>Copy Link</span>
                                {/if}
                            </button>
                        </div>
                    </div>
                </div>

<!-- Add Stusent Manual  -->
            {:else if activeStep === 'manual'}
                <form on:submit|preventDefault={handleManualAdd} class="flex flex-col gap-5" in:fade={{ duration: 250 }}>
                    <div class="space-y-4">
                        <div class="flex flex-col gap-1.5">
                            <label for="studentEmail" class="text-sm font-semibold text-gray-700 dark:text-gray-300">Email Address </label>
                            <input id="studentEmail" type="email" bind:value={studentEmail} placeholder="" required
                                class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-[15px] dark:text-white outline-none transition-all focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10" />
                        </div>
                        <div class="flex flex-col gap-1.5">
                            <label for="studentName" class="text-sm font-semibold text-gray-700 dark:text-gray-300">Student Full Name</label>
                            <input id="studentName" type="text" bind:value={studentName} placeholder=" Mohamed Alami"
                                class="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-[15px] dark:text-white outline-none transition-all focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10" />
                        </div>
                        <button type="submit" disabled={isSubmitting || !studentEmail }
                            class="w-full mt-2 flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-3.5 font-semibold text-white transition-all hover:bg-indigo-700 shadow-lg shadow-indigo-500/20 active:translate-y-px disabled:opacity-50 disabled:cursor-not-allowed">
                            {#if isSubmitting  }
                                <span class="animate-pulse">Processing...</span>
                            {:else}
                                <span>Add Student</span>
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
                            {/if}
                        </button>
                    </div>
                    <div class="flex items-center gap-2 rounded-xl bg-sky-50 dark:bg-sky-900/20 p-3 text-sm text-sky-700 dark:text-sky-300">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>
                        </svg>
                        <span>You can add multiple students one after another</span>
                    </div>
                </form>
            {/if}
        </div>
        
        {#if activeStep === 'selection'}
            <footer class="border-t border-gray-100 dark:border-gray-800 pt-6 text-center" in:fade={{ delay: 300 }}>
                <p class="m-0 flex items-center justify-center gap-1.5 text-sm text-gray-500 dark:text-gray-400">
                    Need help? <a href="/" class="font-semibold text-indigo-600 dark:text-indigo-400 hover:underline">Check our guide</a>
                </p>
            </footer>
        {/if}
    </div>
</div>