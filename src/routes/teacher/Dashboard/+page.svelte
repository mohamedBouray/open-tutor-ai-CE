<script lang="ts">
    import { onMount } from 'svelte';
    import Dashboard from '$lib/components/teacher/pages/Dashboard.svelte';
    import { getMyClasses } from '$lib/apis/classe';
    import { browser } from '$app/environment';

    let ClassOptions: any[] = [];
    let classesError = "";
    let selectedClass = "";

    const getToken = () => (browser ? localStorage.getItem('token') ?? '' : '');
    const token = getToken();

    onMount(async () => {
        try {
            ClassOptions = await getMyClasses(token);
        } catch (err: any) {
            classesError = err || "Failed to load classes";
            console.error(err);
        }
    });
</script>

<div class="mb-[25px] px-[30px]">
    <div class="relative inline-block group">
        <select 
            bind:value={selectedClass}
            class="w-[180px] h-[36px] pl-4 pr-10 border border-gray-300 dark:border-gray-700 rounded-[10px] bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-200 cursor-pointer font-medium text-[13px] outline-none transition-all duration-200 hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-[0_0_0_3px_rgba(59,130,246,0.1)] appearance-none shadow-sm"
        >
            <option value="">All Classes</option>
            {#each ClassOptions as classOption}
                <option value={classOption.id}>
                    {classOption.name} {classOption.course ? `· ${classOption.course}` : ""}
                </option>
            {/each}
        </select>

    </div>

    {#if classesError}
        <span class="ml-4 text-xs text-red-500 font-medium">⚠️ {classesError}</span>
    {/if}
</div>

<Dashboard  />