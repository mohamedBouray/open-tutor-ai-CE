<script lang="ts">
    import Sidebar from '$lib/components/teacher/element/Sidebar.svelte';
    import Header from '$lib/components/teacher/element/Header.svelte';
	import { onMount } from 'svelte';
    import {theme} from '$lib/stores';
    import { get,writable,derived } from 'svelte/store';

    const isDarkMode = derived(theme, ($theme) => {
		return (
			$theme === 'dark' ||
			($theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)
		);
	});

    	let currentIsDarkMode = false;
	isDarkMode.subscribe((value) => {
		currentIsDarkMode = value;
		document.documentElement.classList.toggle('dark', value);
	});
    	function toggleDarkMode(event: CustomEvent) {
		const newTheme = event.detail.isDarkMode ? 'dark' : 'light';
		theme.set(newTheme);
		localStorage.setItem('theme', newTheme);
	}


    onMount(async()=>{
        const currentTheme = get(theme);
        const isDark =
			currentTheme === 'dark' ||
			(currentTheme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
		document.documentElement.classList.toggle('dark', isDark);
    });
</script>
<div class="flex flex-row w-full h-screen m-auto">
    <aside >
        <Sidebar />
    </aside>
    <div class="flex-1 h-screen overflow-hidden w-full flex flex-col bg-[#f8fbff]">
        <header>
            <Header />
        </header>
        <main class="flex-1 overflow-y-auto p-[10px] dark:bg-black">
            <slot />
        </main>
    </div>
</div>

<style>
    :global(body) { margin: 0; padding: 0; overflow: hidden; }
    :global(.dark) {
		color-scheme: dark;
	}
</style>