<script lang="ts">
    import { createEventDispatcher } from 'svelte';
    import { getContext } from 'svelte';
    import type { Writable } from 'svelte/store';

    const dispatch = createEventDispatcher();

    export let selectedClassId: string | number | null = null;
    export let className = "";
    export let courseName = "";

    let newClassName = "";
    let newCourseName = "";
    
    // N-miziw l-values fash kikon edit mode
    $: if (selectedClassId) {
        newClassName = className || "";
        newCourseName = courseName || "";
    }

    // ---- language ----
    interface I18n { t: (key: string) => string; }
    const i18n = getContext<Writable<I18n>>('i18n');

    function closeModal() {
        dispatch('close');
    }
    function AddClass(event?: Event) {
        // Prevent page reload
        if (event) event.preventDefault();

        if (!newClassName.trim() || !newCourseName.trim()) {
            alert($i18n.t('Please fill all fields'));
            return;
        }
        const payload = {
            id: selectedClassId, 
            name: newClassName.toUpperCase(),
            course: newCourseName
        };
        dispatch('save', payload);
        closeModal();
        newClassName = '';
        newCourseName = '';
    }
</script>
<div class="fixed inset-0 z-[1000] flex items-center justify-center bg-slate-900/70 dark:bg-black/80 p-5 backdrop-blur-sm">
    <form action="" on:submit={AddClass}
    class="w-full max-w-[450px] animate-slideIn rounded-[20px] bg-white dark:bg-gray-900 p-[35px] shadow-[0_20px_40px_rgba(0,0,0,0.2)] border border-transparent dark:border-gray-800">
        <h3 class="mb-[25px] mt-0 text-[22px] font-bold text-slate-800 dark:text-white">
            {selectedClassId ? $i18n.t('Edit class') : $i18n.t('Add a new class')}
        </h3>
            <div class="mb-5">
                <label for="ClassName" class="mb-2 block text-sm font-semibold text-slate-600 dark:text-gray-400">
                    {$i18n.t("Class name")}:
                </label>
                <input type="text" id="ClassName" 
                    bind:value={newClassName}
                    placeholder="e.g. GRADE 10"
                    class="w-full rounded-[10px] border border-slate-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-[14px_16px] text-[15px] text-slate-900 dark:text-white transition-all outline-none focus:border-[#667eea] focus:ring-3 focus:ring-[#667eea]/15"/>
            </div>

            <div class="mb-5">
                <label for="CoursName" class="mb-2 block text-sm font-semibold text-slate-600 dark:text-gray-400">
                    {$i18n.t("Course name")}:
                </label>
                <input type="text" id="CoursName" 
                    bind:value={newCourseName} 
                    placeholder="e.g. Mathematics"
                    class="w-full rounded-[10px] border border-slate-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-[14px_16px] text-[15px] text-slate-900 dark:text-white transition-all outline-none focus:border-[#667eea] focus:ring-3 focus:ring-[#667eea]/15"/>
            </div>

            <div class="mt-[30px] flex justify-end gap-[15px]">
                <button  type="button" class="rounded-[10px] bg-slate-100 dark:bg-gray-800 px-6 py-3 text-sm font-semibold text-slate-600 dark:text-gray-300 transition-all hover:bg-slate-200 dark:hover:bg-gray-700" 
                    on:click={closeModal}>
                    {$i18n.t("Annuler")}
                </button>
                
                <button type="submit" class="rounded-[10px] bg-gradient-to-br from-[#667eea] to-[#764ba2] px-[28px] py-3 text-sm font-semibold text-white transition-all hover:-translate-y-0.5 active:scale-95 hover:shadow-[0_6px_20px_rgba(102,126,234,0.3)]" 
                    >
                    {selectedClassId ? $i18n.t('Modifier') : $i18n.t('Créer')}
                </button>
            </div>
    </form>
</div>

<style>
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .animate-slideIn {
        animation: slideIn 0.3s ease forwards;
    }
</style> 