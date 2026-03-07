<script lang="ts">
	import AssignementModal from '$lib/components/teacher/element/AssignementModal.svelte';
    import Assignments from '$lib/components/student/pages/Assignments.svelte';
    import updateIcon from '$lib/components/icons/Pencil.svelte';
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { browser } from '$app/environment';
	import { getMyAssignment, createNewAssignment ,deleteAssignmentById , updateAssignment , getAssignmentStats} from '$lib/apis/assignment';
	import type { AssignmentResponse, AssignmentCreateRequest } from '$lib/apis/assignment';
	import type { Writable } from 'svelte/store';

    let stats = {
        total: 0,
        pending: 0,
        avg_rate: '0%',
        completion: '0%',
        total_change: '0%',
        avg_rate_change: '0%',
        pending_change: '0%',
        completion_change: '0%'
    };
    
	let showAssignementModal: boolean = false;
	let selectedAssignmentData: AssignmentCreateRequest | null = null;
    let selectedAssignmentId: string | null = null;

    let showMoreDropdown: string | number | null = null;
	let loading = true;
    let Assignements: AssignmentResponse[] = [];

   $:StatsMenu= [
            { label: 'Total Assignments', value: stats.total, change: stats.total_change }, 
            { label: 'Avg Submission Rate', value: stats.avg_rate,change: stats.avg_rate_change }, 
            { label: 'Pending Review', value: stats.pending, change: stats.pending_change }, 
            { label: 'Completion Rate', value: stats.completion, change: stats.completion_change }
        ] ;
	const getToken = () => (browser ? (localStorage.getItem('token') ?? '') : '');
    
    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

	function openModal() {showAssignementModal = true; selectedAssignmentId = null;selectedAssignmentData = null;}
	function MoreDropdown(id: string | number) {showMoreDropdown = showMoreDropdown === id ? null : id;}
    function closeAllDropdowns() {showMoreDropdown = null;}


    // ===== Save Assignment (Create or Update) ====
	async function SaveAssignment(event: CustomEvent<{title: string;description: string; classe_id: string;  deadline: Date; points: number;}>) {
		const AssignmentData = event.detail;
		const token = getToken();
		console.log('TOKEN SENT:', token);
		console.log('DATA SENT:', AssignmentData);

		if (!token) {
			toast.error($i18n.t('Session expired, please login again'));
			return;
		}
		try {
            if (selectedAssignmentId) {
                await updateAssignment(token, selectedAssignmentId, AssignmentData);
                toast.success($i18n.t('Class updated successfully'));
            } else {
			    const newCreatedAssignment = await createNewAssignment(token, AssignmentData);
			    toast.success($i18n.t('Assignment created successfully'));
            }
			await loadAssignment();
            await loadStats();
            showAssignementModal= false;
	        selectedAssignmentData = null;
            selectedAssignmentId = null;
		} catch (err: any) {
			console.error(err);
			toast.error($i18n.t('Error saving assignment'));
		}
	}

    // === Modify Assignment ====
    function ModifyAssignment(assignmentId: string): void {
        const assignment = Assignements.find(c => c.id === assignmentId);
        if (assignment) {
            selectedAssignmentId = assignment.id;
            selectedAssignmentData = { ...assignment }; 
            showAssignementModal = true;
            closeAllDropdowns();
        }
    }

    // ===== Delete Assignment ====
    async function DeleteAssignment(assignmentId: string) {
        if (confirm($i18n.t('Do you really want to remove this assignment ?'))) {
            try {
                const token = getToken();
                await deleteAssignmentById(token, assignmentId);
                Assignements = Assignements.filter(c => c.id !== assignmentId);
                await loadStats();
                toast.success($i18n.t('Class deleted successfully'));
                closeAllDropdowns();
            } catch (err) {
                toast.error($i18n.t('Error during deletion'));
            }
        }
    }

    // ===== Load Assignments ====
	async function loadAssignment() {
		const token = getToken();
		if (!token) return;
		loading = true;
		try {
			Assignements = await getMyAssignment(token);
			console.log(Assignments.length);
		} catch (err: any) {
			console.error('Erreur fetching assignments:', err);
			toast.error($i18n.t('Failed to load assignments'));
		} finally {
			loading = false;
		}
	}

    // ==== Load Stats ====
    async function loadStats() {
        const token = getToken();
        try {
            stats = await getAssignmentStats(token);
        } catch (err) {
            console.error("Failed to load stats", err);
        }
    }

    $: sortedAssignments = [...Assignements].sort((a, b) => {
        const priority: { [key: string]: number } = { 'Active': 1, 'Pending': 2, 'Completed': 3 };
        return (priority[a.status] || 0) - (priority[b.status] || 0);
});

	onMount(() => {
		loadAssignment();
        loadStats(); 
		const handleClickOutside = (event: MouseEvent) => {
			const target = event.target as HTMLElement;
			if (!target.closest('.more-container')) {
				showMoreDropdown = null;
			}
		};
		document.addEventListener('click', handleClickOutside);
		return () => {
			document.removeEventListener('click', handleClickOutside);
		};
	});
</script>

<main class="m-0 p-[30px] pt-0 bg-[#f8fafc] dark:bg-gray-950 min-h-screen transition-colors duration-200">
    <div class="flex flex-row justify-between gap-[20px]">
        {#each StatsMenu as stat}
            <div
                class="w-[219px] h-[108px] bg-white dark:bg-gray-900 rounded-[27px] border border-[#f1f5f9] dark:border-gray-800 shadow-[0_1px_3px_rgba(0,0,0,0.05)] transition-all duration-300 hover:-translate-y-[5px] hover:shadow-[0_10px_30px_rgba(0,0,0,0.1)] p-[20px] box-border">
                <p class="text-[#45484e] dark:text-gray-400 font-['Inter'] text-[14px] font-normal opacity-100">
                    {stat.label}
                </p>
                <h3 class="py-[10px] text-[24px] font-bold font-['Inter'] leading-none text-[#0F172A] dark:text-white">
                    {stat.value}
                </h3>
                <p class="font-['Inter'] font-normal text-[12px] leading-none text-[#22C55E] text-right">
                    {stat.change}
                </p>
            </div>
        {/each}
    </div>

    <div class="flex justify-end mt-[20px]">
        <button class="bg-[#3B82F6] text-white border-none py-[10px] px-[20px] rounded-[15px] text-[16px] cursor-pointer transition-colors duration-300 hover:bg-[#2563EB]"
            on:click={openModal}>
            {$i18n.t('Create Assignment')}
        </button>
        {#if showAssignementModal}
            <AssignementModal
                assignmentId={selectedAssignmentId}
                title={selectedAssignmentData?.title || ''}
                description={selectedAssignmentData?.description || ''}
                classe_id={selectedAssignmentData?.classe_id || ''}
                deadline={selectedAssignmentData?.deadline || ''}
                points={selectedAssignmentData?.points || 0}
                on:close={() => {
                    showAssignementModal = false;
                    selectedAssignmentData = null;
                }}
                on:save={SaveAssignment}
            />
        {/if}
    </div>

    <div class="mt-[30px]">
        {#each Assignements as assignment (assignment.id)}
            <div class="bg-white dark:bg-gray-900 border border-[#F3F4F6] dark:border-gray-800 rounded-[12px] p-[24px] mb-[16px] font-['Inter'] transition-all duration-200 cursor-pointer hover:-translate-y-[4px] hover:shadow-[0_12px_20px_-5px_rgba(0,0,0,0.05)] hover:border-[#DBEAFE] dark:hover:border-blue-900">
                <div class="flex justify-between items-start">
                    <div class="flex-grow mr-[16px]">
                        <h3 class="text-[1.1rem] font-semibold text-[#111827] dark:text-white mb-[4px]">{assignment.title}</h3>
                        <p class="text-[0.85rem] text-[#6B7280] dark:text-gray-400 m-0">{assignment.description}</p>
                    </div>

                    <div class="flex items-center gap-[30px]">
                        <div class="flex items-center gap-[6px] px-[12px] py-[4px] rounded-[20px] text-[0.75rem] font-medium 
                            {assignment.status === 'Active' ? 'bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400' : 
                            assignment.status === 'Pending' ? 'bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400' : 
                            'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400'}">
                            
                            <span class="w-[6px] h-[6px] rounded-full bg-current"></span>
                            {$i18n.t(assignment.status)}
                        </div>

                        <div class="relative more-container">
                            <button class="bg-none border-none text-[#9CA3AF] hover:text-gray-600 dark:hover:text-white cursor-pointer text-xl"
                                on:click|stopPropagation={() => MoreDropdown(assignment.id)}
                                aria-label="More options">⋮</button>
                            {#if showMoreDropdown === assignment.id}
                                <div class="absolute top-[40px] right-0 bg-white dark:bg-gray-800 border border-[#E5E7EB] dark:border-gray-700 rounded-[8px] shadow-[0_4px_12px_rgba(0,0,0,0.1)] z-10 w-[150px] overflow-hidden">
                                    <button class="flex items-center gap-[8px] w-full px-[16px] py-[10px] text-[0.9rem] text-[#EF4444] cursor-pointer hover:bg-[#FEE2E2] dark:hover:bg-red-900/20 border-none bg-transparent"
                                        on:click|stopPropagation={() => DeleteAssignment(assignment.id)}>
                                        <img src="/teacher/supprimer.png" alt="" class="w-[16px] h-[16px] dark:invert"/> 
                                        {$i18n.t('Delete')}
                                    </button>
                                    <button class="flex items-center gap-[8px] w-full px-[16px] py-[10px] text-[0.9rem] text-blue-600 dark:text-blue-400 cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20 border-none bg-transparent"
                                        on:click|stopPropagation={() => ModifyAssignment(assignment.id)}>
                                        <span>
                                            <svelte:component this = {updateIcon}/>
                                        </span> 
                                        {$i18n.t('Update')}
                                    </button>
                                </div>
                            {/if}
                        </div>
                    </div>
                </div>

                <div class="flex gap-[20px] mt-[12px] text-[0.8rem] text-[#6B7280] dark:text-gray-400">
                    <span>📚 {assignment.classe_name}</span>
                    <span>🗓️ {$i18n.t('Due')}: {new Date(assignment.deadline).toLocaleDateString('en-GB')}</span>
                </div>

                <hr class="border-0 border-t border-[#F3F4F6] dark:border-gray-800 my-[20px]" />

               <div class="flex gap-[48px] items-center">
                    <div class="flex flex-col gap-[4px]">
                        <span class="text-[0.75rem] text-[#9CA3AF]">{$i18n.t('Submissions')}</span>
                        <span class="text-[0.9rem] font-semibold text-[#111827] dark:text-white">
                            {Math.min(assignment.current_submissions, assignment.max_submissions)}/ {assignment.max_submissions}
                        </span>
                    </div>
                    
                    <div class="flex-grow max-w-[300px]">
                        <div class="flex justify-between mb-[8px]">
                            <span class="text-[0.75rem] text-[#9CA3AF]">{$i18n.t('Submission Rate')}</span>
                            <span class="text-[0.9rem] font-semibold text-[#111827] dark:text-white">
                                {assignment.max_submissions > 0 
                                    ? Math.min(Math.round((assignment.current_submissions / assignment.max_submissions) * 100), 100) 
                                    : 0}%
                            </span>
                        </div>
                        <div class="h-[8px] bg-[#F3F4F6] dark:bg-gray-800 rounded-[4px] overflow-hidden">
                            <div class="h-full bg-[#3B82F6] transition-all duration-300"
                                style="width: {assignment.max_submissions > 0 
                                    ? Math.min((assignment.current_submissions / assignment.max_submissions) * 100, 100) 
                                    : 0}%">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {:else}
            <div class="flex flex-col items-center justify-center p-[60px_20px] bg-white dark:bg-gray-900 border-2 border-dashed border-[#E2E8F0] dark:border-gray-800 rounded-[24px] text-center mt-[40px] group">
                <div class="bg-[#F8FAFC] dark:bg-gray-800 text-[#94A3B8] w-[100px] h-[100px] rounded-full flex items-center justify-center mb-[20px] transition-transform duration-300 group-hover:scale-110 group-hover:rotate-6 group-hover:text-[#3B82F6]">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17"/>
                        <line x1="10" y1="9" x2="8" y2="9"/>
                    </svg>
                </div>
                <h3 class="text-[1.25rem] font-semibold text-[#1E293B] dark:text-white mb-[8px]">{$i18n.t('No assignments yet')}</h3>
                <p class="text-[#64748B] dark:text-gray-400 max-w-[320px] text-[0.95rem] leading-[1.5] mb-[24px]">
                   {$i18n.t('Your workspace is looking a bit empty. Start by creating your first assignment!')}
                </p>
                <button class="bg-[#EFF6FF] dark:bg-blue-900/30 text-[#3B82F6] dark:text-blue-400 border-none py-[10px] px-[20px] rounded-[12px] font-semibold cursor-pointer flex items-center gap-[8px] transition-all hover:bg-[#DBEAFE] dark:hover:bg-blue-900/50"
                    on:click={openModal}>
                    <span>+</span> {$i18n.t('Quick Create')}
                </button>
            </div>
        {/each}
    </div>
</main>