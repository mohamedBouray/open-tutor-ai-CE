<script lang="ts">
	import { onMount } from 'svelte';
	import { createEventDispatcher } from 'svelte';
	import { browser } from '$app/environment';
	import { getMyClasses } from '$lib/apis/classe';

	const dispatch = createEventDispatcher();
	const getToken = () => (browser ? (localStorage.getItem('token') ?? '') : '');
	const token = getToken();
	function closeModal() {
		dispatch('close');
	}

	export let assignmentId: string | number | null = null;
	export let title = '';
	export let description = '';
	export let classe_id = '';
	export let deadline;
	export let points = 0;

	let assignmentTitle = title;
	let assignmentDescription = description;
	let assignmentClass = classe_id;
	let assignmentDueDate = deadline;
	let assignmentMaxPoints = points;

	let ClassOptions: any[] = [

	];
	let assignmentsError = '';

	$: {
		assignmentTitle = title || '';
		assignmentDescription = description || '';
		assignmentClass = classe_id || '';
		assignmentDueDate = deadline || '';
		assignmentMaxPoints = points || 0;
	}

	// Add Assignment
	async function AddAssignment() {
		// if (!assignmentTitle.trim() || !assignmentDescription.trim()  || !assignmentDueDate.trim() || assignmentMaxPoints <= 0) {
		//     alert('Please fill all fields');
		//     return ;
		// }
		const payload = {
			title: assignmentTitle,
			description: assignmentDescription,
			classe_id: assignmentClass,
			deadline: assignmentDueDate,
			points: assignmentMaxPoints
		};
		dispatch('save', payload);
		closeModal();
	}

	onMount(async () => {
		try {
			ClassOptions = await getMyClasses(token);
		} catch (err: any) {
			assignmentsError = err || 'Failed to load assignments';
			console.error(err);
		}
	});
</script>

<main
    class="fixed inset-0 z-[1000] flex items-center justify-center bg-slate-900/70 dark:bg-black/80 p-5 backdrop-blur-sm transition-all"
>
    <div
        class="flex max-h-[90vh] w-full max-w-[520px] origin-center animate-pop flex-col overflow-hidden rounded-[24px] bg-white dark:bg-gray-900 p-8 shadow-2xl transition-colors duration-200"
    >
        <div class="flex flex-shrink-0 items-center justify-between border-b border-gray-200 dark:border-gray-800 pb-4">
            <h2 class="m-0 text-xl font-semibold text-gray-900 dark:text-white">
                {assignmentId ? 'Modifier l-Assignment' : 'Créer un Assignment'}
            </h2>
            <button
                class="flex h-8 w-8 items-center justify-center rounded-lg bg-transparent text-gray-500 transition-all hover:rotate-90 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white"
                on:click={() => dispatch('close')}
                aria-label="Close"
            >
                <svg
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                >
                    <path d="M18 6L6 18M6 6l12 12" />
                </svg>
            </button>
        </div>

        <div class="flex-grow overflow-y-auto py-6 font-['Inter']">
            <div class="mb-5 flex flex-col gap-2">
                <label for="title" class="text-sm font-medium text-gray-700 dark:text-gray-300">Assignment Title</label>
                <input
                    id="title"
                    type="text"
                    placeholder="Enter assignment title"
                    bind:value={assignmentTitle}
                    class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-[15px] text-gray-900 dark:text-white outline-none transition-all focus:border-blue-500 focus:ring-3 focus:ring-blue-500/10"
                />
            </div>

            <div class="mb-5 flex flex-col gap-2">
                <label for="desc" class="text-sm font-medium text-gray-700 dark:text-gray-300">Description</label>
                <textarea
                    id="desc"
                    rows="4"
                    bind:value={assignmentDescription}
                    class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-[15px] text-gray-900 dark:text-white outline-none transition-all focus:border-blue-500 focus:ring-3 focus:ring-blue-500/10"
                    placeholder="Enter assignment description..."
                ></textarea>
            </div>

            <div class="mb-5 flex flex-col gap-2">
                <label for="class" class="text-sm font-medium text-gray-700 dark:text-gray-300">Class</label>
                <select
                    id="class"
                    bind:value={assignmentClass}
                    class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-[15px] text-gray-900 dark:text-white outline-none transition-all focus:border-blue-500"
                >
                    <option value="" disabled selected>Choose option...</option>
                    {#each ClassOptions as classOption}
                        <option value={classOption.id} class="bg-white dark:bg-gray-800">
                            {classOption.name}
                            {classOption.course ? `- ${classOption.course}` : ''}
                        </option>
                    {/each}
                </select>
            </div>

            <div class="grid grid-cols-2 gap-4 mb-5">
                <div class="flex flex-col gap-2">
                    <label for="date" class="text-sm font-medium text-gray-700 dark:text-gray-300">Due Date</label>
                    <input
                        id="date"
                        type="date"
                        bind:value={assignmentDueDate}
                        class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-[15px] text-gray-900 dark:text-white outline-none focus:border-blue-500"
                    />
                </div>
                <div class="flex flex-col gap-2">
                    <label for="points" class="text-sm font-medium text-gray-700 dark:text-gray-300">Max Points</label>
                    <input
                        id="points"
                        type="number"
                        min="0"
                        bind:value={assignmentMaxPoints}
                        class="rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 p-3 text-[15px] text-gray-900 dark:text-white outline-none focus:border-blue-500"
                    />
                </div>
            </div>

            <div class="mt-4 flex gap-3">
                <button
                    class="flex-1 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 py-3 text-[15px] font-semibold text-gray-700 dark:text-gray-300 transition-all hover:bg-gray-50 dark:hover:bg-gray-700"
                    on:click={closeModal}
                >
                    Cancel
                </button>
                <button
                    class="flex-1 rounded-lg border-none bg-blue-600 py-3 text-[15px] font-semibold text-white transition-all hover:bg-blue-700 active:scale-[0.98]"
                    on:click={AddAssignment}
                >
                    {assignmentId ? 'Modifier' : 'Créer'} Assignment
                </button>
            </div>
        </div>
    </div>
</main>

<style>
    @keyframes slideIn {
        from { 
            opacity: 0; 
            transform: translateY(-30px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }
	.animate-pop {
		animation: slideIn 0.3s ease-out;
	}
</style>