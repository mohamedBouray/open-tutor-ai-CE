<script lang="ts">
    import { getMyClasses, getStudentsByClassId } from '$lib/apis/classe';
    import { onMount, getContext } from 'svelte';
    import { browser } from '$app/environment';
    import type { Writable } from 'svelte/store';
    import { toast } from 'svelte-sonner';
    import { fly } from 'svelte/transition';

    // ==== Languages ====
    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    let classes: any[] = [];
    let allEnrollments: any[] = [];
    let selectedClassId: string = 'all';
    let loading = true;
    
    const getToken = () => (browser ? localStorage.getItem('token') ?? '' : '');

    $: filteredStudents = (() => {
        let studentsMap = new Map();
        let dataToProcess = selectedClassId === 'all' ? allEnrollments 
            : allEnrollments.filter(en => en.classId === selectedClassId);

        dataToProcess.forEach(en => {
            if (!en.user) return;
            const studentId = en.user.id;
            
            if (!studentsMap.has(studentId)) {
                studentsMap.set(studentId, {
                    name: en.user.name,
                    email: en.user.email,
                    avatar: en.user.profile_image_url || `https://ui-avatars.com/api/?name=${en.user.name}&background=random`,
                    points: 0,
                    courseCount: 0
                });
            }
            let s = studentsMap.get(studentId);
            s.points += en.points || 0;
            s.courseCount += 1;
        });

        return Array.from(studentsMap.values())
            .sort((a, b) => b.points - a.points)
            .map((s, i) => ({ ...s, rank: i + 1 }));
    })();

    async function loadData() {
        const token = getToken();
        if (!token) return;
        try {
            loading = true;
            classes = await getMyClasses(token);
            const promises = classes.map(async (cls) => {
                try {
                    const students = await getStudentsByClassId(token, cls.id);
                    return students.map((s: any) => ({ ...s, classId: cls.id }));
                } catch (e) { return []; }
            });
            const results = await Promise.all(promises);
            allEnrollments = results.flat();
        } catch (err) {
            console.error("Error loading students:", err);
            toast.error($i18n.t('Failed to load students'));
        } finally {
            loading = false;
        }
    }
    onMount(loadData);
</script>
<div class="p-5 bg-[#f8fafc] dark:bg-black min-h-screen transition-colors duration-300 font-['Inter']">
    
    <div class="max-w-7xl mx-auto bg-white dark:bg-[#0a0a0a] rounded-[24px] shadow-sm border border-slate-200 dark:border-white/10 overflow-hidden">
        
        <div class="p-6 border-b border-slate-100 dark:border-white/5 flex flex-col sm:flex-row justify-between items-center gap-4 bg-white dark:bg-[#0a0a0a]">
            <div class="flex items-center gap-4">
                <div class="p-2.5 bg-indigo-600 rounded-xl text-white shadow-lg shadow-indigo-500/20">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/></svg>
                </div>
                <div>
                    <h3 class="text-lg font-black text-slate-800 dark:text-white m-0 uppercase tracking-tight">
                        {$i18n.t('Leaderboard')}
                    </h3>
                    <p class="text-[12px] text-slate-400 dark:text-gray-500 font-medium leading-none mt-1">{$i18n.t('Top performing students')}</p>
                </div>
            </div>

            <div class="relative min-w-[220px] group">
                <select bind:value={selectedClassId}
                    class="w-full bg-slate-50 dark:bg-white/5 text-slate-700 dark:text-white py-2.5 pl-10 pr-10 rounded-xl border border-slate-200 dark:border-white/10 shadow-sm outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all cursor-pointer appearance-none font-semibold text-sm">
                    <option value="all" class="dark:bg-black">🌐 {$i18n.t('Global Ranking')}</option>
                    {#each classes as cls}
                        <option value={cls.id} class="dark:bg-black">📚 {cls.name}</option>
                    {/each}
                </select>
                <div class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
                </div>
            </div>
        </div>

        {#if loading}
            <div class="flex flex-col items-center justify-center p-32 bg-white dark:bg-[#0a0a0a]">
                <div class="relative w-12 h-12">
                    <div class="absolute inset-0 rounded-full border-4 border-indigo-500/10"></div>
                    <div class="absolute inset-0 rounded-full border-4 border-t-indigo-600 animate-spin"></div>
                </div>
                <p class="mt-6 text-slate-400 dark:text-gray-600 text-sm font-bold animate-pulse uppercase tracking-widest">{$i18n.t('Syncing Data...')}</p>
            </div>
        {:else}
            <div class="overflow-x-auto bg-white dark:bg-[#0a0a0a]">
                <table class="w-full border-separate border-spacing-0">
                    <thead>
                        <tr class="bg-slate-50/50 dark:bg-white/[0.02]">
                            <th class="py-4 px-8 text-left text-[10px] font-black text-slate-400 dark:text-gray-500 uppercase tracking-widest">Rank</th>
                            <th class="py-4 px-8 text-left text-[10px] font-black text-slate-400 dark:text-gray-500 uppercase tracking-widest">Student</th>
                            <th class="py-4 px-8 text-center text-[10px] font-black text-slate-400 dark:text-gray-500 uppercase tracking-widest">Activity</th>
                            <th class="py-4 px-8 text-right text-[10px] font-black text-slate-400 dark:text-gray-500 uppercase tracking-widest">Points</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-100 dark:divide-white/5">
                        {#each filteredStudents as student, i (student.name)}
                            <tr in:fly={{ y: 15, delay: i * 40 }} class="group hover:bg-slate-50 dark:hover:bg-white/[0.03] transition-all duration-200">
                                <td class="py-5 px-8">
                                    <div class="flex items-center gap-3">
                                        <span class="w-9 h-9 flex items-center justify-center rounded-xl 
                                            {student.rank === 1 ? 'bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400 border border-amber-200 dark:border-amber-500/30' : 
                                             student.rank === 2 ? 'bg-slate-100 text-slate-600 dark:bg-white/10 dark:text-gray-300' : 
                                             student.rank === 3 ? 'bg-orange-50 text-orange-600 dark:bg-orange-500/20 dark:text-orange-400' : 
                                             'bg-slate-50 dark:bg-white/5 text-slate-400 dark:text-gray-500'} 
                                            font-black text-sm shadow-sm transition-transform group-hover:scale-110">
                                            {student.rank}
                                        </span>
                                    </div>
                                </td>
                                <td class="py-5 px-8">
                                    <div class="flex items-center gap-4">
                                        <div class="relative shrink-0">
                                            <img src={student.avatar} alt="" class="w-11 h-11 rounded-2xl object-cover ring-4 ring-white dark:ring-[#111] shadow-sm" />
                                            {#if student.rank === 1}
                                                <div class="absolute -top-2 -right-2 bg-white dark:bg-black rounded-full w-5 h-5 flex items-center justify-center shadow-md border border-amber-100 dark:border-amber-900/50 text-[10px]">👑</div>
                                            {/if}
                                        </div>
                                        <div class="flex flex-col min-w-0">
                                            <span class="font-bold text-slate-800 dark:text-gray-100 text-sm truncate">{student.name}</span>
                                            <span class="text-[11px] text-slate-400 dark:text-gray-500 truncate font-medium">{student.email}</span>
                                        </div>
                                    </div>
                                </td>
                                <td class="py-5 px-8 text-center">
                                    <span class="inline-flex items-center px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-500/20 text-indigo-600 dark:text-indigo-400 text-[10px] font-black uppercase tracking-tight">
                                        {student.courseCount} Classes
                                    </span>
                                </td>
                                <td class="py-5 px-8 text-right">
                                    <div class="flex flex-col items-end">
                                        <div class="flex items-center gap-1.5">
                                            <span class="text-lg font-black text-emerald-600 dark:text-emerald-400 tabular-nums">
                                                {student.points.toLocaleString()}
                                            </span>
                                            <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                                        </div>
                                        <span class="text-[8px] font-black text-slate-300 dark:text-gray-600 uppercase tracking-widest">Total XP</span>
                                    </div>
                                </td>
                            </tr>
                        {:else}
                            <tr>
                                <td colspan="4" class="py-24 text-center">
                                    <div class="flex flex-col items-center opacity-30">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="mb-3 text-slate-500"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="17" y1="8" x2="22" y2="13"/><line x1="22" y1="8" x2="17" y2="13"/></svg>
                                        <p class="text-slate-500 font-bold text-sm tracking-tight">{$i18n.t('No student data available')}</p>
                                    </div>
                                </td>
                            </tr>
                        {/each}
                    </tbody>
                </table>
            </div>
        {/if}
    </div>
</div>

<style>
    .overflow-x-auto::-webkit-scrollbar {
        height: 5px;
    }
    .overflow-x-auto::-webkit-scrollbar-track {
        background: transparent;
    }
    .overflow-x-auto::-webkit-scrollbar-thumb {
        background: #e2e8f0;
        border-radius: 20px;
    }
    :global(.dark) .overflow-x-auto::-webkit-scrollbar-thumb {
        background: #333; /* Scrollbar dark m9ad */
    }
    
    tr {
        contain: content;
    }
</style>