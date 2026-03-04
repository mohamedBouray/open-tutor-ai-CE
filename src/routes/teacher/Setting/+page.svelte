<script lang="ts">
    import { onMount , getContext} from 'svelte';
    import { toast } from 'svelte-sonner';
    import { user ,theme  } from '$lib/stores'; 
    import { getGravatarUrl } from '$lib/apis/utils';
    import { generateInitialsImage } from '$lib/utils';
    import { updateUserPassword } from '$lib/apis/auths';
    import { updateUserProfile, getSessionUser } from '$lib/apis/auths';
    import {getLanguages} from '$lib/i18n';
    
    import { type Writable } from 'svelte/store';
    import type { i18n as i18nType } from 'i18next';

    export let saveHandler: Function = () => {};

    let profileImageInputElement: HTMLInputElement;
    $: $user = $user;
    let name: string = '';
    let profileImageUrl: string = '';

    let show = false;
    let currentPassword = '';
    let newPassword = '';
    let newPasswordConfirm = '';

    let i18n = getContext<Writable<i18nType>>('i18n'); 
    let languages: Awaited<ReturnType<typeof getLanguages>> = [];
    let lang =$i18n.language;

    let themes = ['system', 'dark', 'light'];
    let selectedTheme = 'light';
    

// --- Upload Images ---
    const handleImageChange = (e: Event) => {
        const files = profileImageInputElement.files;
        if (!files || files.length === 0) 
            return;

        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.src = event.target?.result as string;
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 250;
                canvas.height = 250;
                
                const aspectRatio = img.width / img.height;
                let newW = 250, newH = 250;
                if (aspectRatio > 1) newH = 250 / aspectRatio; else newW = 250 * aspectRatio;

                ctx?.drawImage(img, (250 - newW) / 2, (250 - newH) / 2, newW, newH);
                profileImageUrl = canvas.toDataURL('image/jpeg', 0.8);
            };
        };
        reader.readAsDataURL(files[0]);
    };


//  --- Buttons Profil Actions ---
    const setInitials = () => {
        profileImageUrl = generateInitialsImage(name || $user?.name || '');
    };

    const setGravatar = async () => {
        try {
            const url = await getGravatarUrl(localStorage.token, $user?.email || '');
            if (url) {
                profileImageUrl = url;
                toast.success("Gravatar profile image loaded!");
            } else {
                toast.error("No Gravatar found for this email.");
            }
        } catch (e) {
            toast.error("Couldn't fetch Gravatar");
        }
    };

    const removeImage = () => {
        profileImageUrl = '/user.png';
    };


// ---Update password Section ---
    const updatePasswordHandler = async () => {
        if (newPassword === newPasswordConfirm) {
            const res = await updateUserPassword(localStorage.token, currentPassword, newPassword).catch(
                (error) => {
                    toast.error(`${error}`);
                    return null;
                }
            );
            if (res) {
                toast.success('Successfully updated.');
            }
            currentPassword = '';
            newPassword = '';
            newPasswordConfirm = '';
        } else {
            toast.error(
                `The passwords you entered don't quite match. Please double-check and try again.`
            );
            newPassword = '';
            newPasswordConfirm = '';
        }
    };


// --Change theme section ---
    const applyTheme = (_theme: string) => {
        let themeToApply = _theme === 'oled-dark' ? 'dark' : _theme;

        if (_theme === 'system') {
            themeToApply = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        }

        themes
            .filter((e) => e !== themeToApply)
            .forEach((e) => {
                e.split(' ').forEach((cls) => document.documentElement.classList.remove(cls));
            });

        themeToApply.split(' ').forEach((cls) => document.documentElement.classList.add(cls));
    };

    const themeChangeHandler = (_theme: string) => {
        theme.set(_theme); 
        localStorage.setItem('theme', _theme); 
        applyTheme(_theme); 
        selectedTheme = _theme;
    };




    const submitHandler = async () => {
		if (name !== $user?.name) {
			if (profileImageUrl === generateInitialsImage($user?.name) || profileImageUrl === '') {
				profileImageUrl = generateInitialsImage(name);
			}
		}

		const updatedUser = await updateUserProfile(localStorage.token, name, profileImageUrl).catch(
			(error) => {
				toast.error(`${error}`);
			}
		);

		if (updatedUser) {
			// Get Session User Info
			const sessionUser = await getSessionUser(localStorage.token).catch((error) => {
				toast.error(`${error}`);
				return null;
			});

			await user.set(sessionUser);
			return true;
		}
		return false;
	};



//  --- On Mount ---
onMount(async() => {
    name = $user?.name || '';
    profileImageUrl = $user?.profile_image_url || '/user.png';

    selectedTheme =localStorage.theme ?? 'system';
    applyTheme(selectedTheme);

    languages = await getLanguages();
    lang = $i18n.language;
});
</script>
<div class="flex flex-col bg-[#F8FAFC] dark:bg-gray-950 text-[#334155] dark:text-gray-200 p-[20px] font-sans w-full gap-[1.2rem] transition-colors duration-200">

    <section class="flex gap-[2.3rem] bg-white dark:bg-gray-900 p-[1.5rem] rounded-[1.2rem] border border-[#e2e8f0] dark:border-gray-800 items-center">
        <input type="file" hidden accept="image/*" bind:this={profileImageInputElement} on:change={handleImageChange} />
        
        <div class="relative flex-shrink-0">
            <div class="w-[100px] h-[100px] rounded-full overflow-hidden border-[3px] border-[#4881db] bg-[#f1f5f9] dark:bg-gray-800">
                <img src={profileImageUrl || '/user.png'} alt="Profile" class="w-full h-full object-cover"/>
            </div>
            <button 
                class="absolute bottom-[2px] right-[2px] bg-[#3B82F6] text-white border-2 border-white dark:border-gray-900 rounded-full p-[4px] cursor-pointer shadow-md transition-all duration-200 hover:bg-[#2563eb] hover:scale-110" 
                type="button" 
                on:click={() => profileImageInputElement.click()} 
                title="Change Profile Picture">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
                stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                    <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
                    <circle cx="12" cy="13" r="3"/>
                </svg>
            </button>
        </div>

        <div class="flex-grow">
            <h3 class="text-[14px] font-semibold text-[#5a6677] dark:text-gray-400 mb-2"> {$i18n.t('Profile Image')}</h3>
            <div class="flex gap-2 mb-5 flex-wrap">
                <button class="bg-[#f1f5f9] dark:bg-gray-800 border border-[#e2e8f0] dark:border-gray-700 px-3 py-1.5 rounded-lg text-xs text-[#334155] dark:text-gray-300 cursor-pointer hover:bg-[#e2e8f0] dark:hover:bg-gray-700" type="button" on:click={setInitials}>{$i18n.t('Use Initials')}</button>
                <button class="bg-[#f1f5f9] dark:bg-gray-800 border border-[#e2e8f0] dark:border-gray-700 px-3 py-1.5 rounded-lg text-xs text-[#334155] dark:text-gray-300 cursor-pointer hover:bg-[#e2e8f0] dark:hover:bg-gray-700" type="button" on:click={setGravatar}>{$i18n.t('Use Gravatar')}</button>
                <button class="bg-[#fff1f2] dark:bg-red-900/20 border border-[#fecaca] dark:border-red-900/30 px-3 py-1.5 rounded-lg text-xs text-[#ef4444] cursor-pointer hover:bg-red-50 dark:hover:bg-red-900/40" type="button" on:click={removeImage}>{$i18n.t('Remove')}</button>
            </div>

            <div class="mb-4 w-full">
                <label class="block text-xs font-semibold text-[#5a6677] dark:text-gray-400 mb-1.5" for="fullname">{$i18n.t('Full Name')}</label>
                <input id="fullname" type="text" class="w-full px-3.5 py-2.5 rounded-xl border border-[#e2e8f0] dark:border-gray-700 bg-white dark:bg-gray-800 text-[#334155] dark:text-white outline-none focus:border-[#3B82F6] focus:ring-1 focus:ring-[#3B82F6]" bind:value={name} required/>
            </div>
        </div>
    </section>

    <section class="bg-white dark:bg-gray-900 p-6 pb-2.5 rounded-[1.2rem] border border-[#e2e8f0] dark:border-gray-800 transition-all">
        <div class="flex justify-between items-center mb-4">
            <div class="text-base font-semibold text-[#1e293b] dark:text-gray-100"> {$i18n.t('Change Password')}</div>
            <button class="bg-none border-none text-[#3B82F6] text-sm cursor-pointer px-3 py-1.5 rounded-lg transition-colors duration-200 hover:bg-blue-50 dark:hover:bg-blue-900/20" type="button" on:click={() => {show = !show;}}>
                {show ? '▲' :'▼'}
            </button>
        </div>

        {#if show}
            <div class="flex items-center gap-2.5 mb-6">
                <span class="text-lg">🔒</span>
                <h3 class="text-base m-0 text-[#1e293b] dark:text-gray-200">{$i18n.t('Security & Password')}</h3>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="mb-4 w-full">
                    <label class="block text-xs font-semibold text-[#5a6677] dark:text-gray-400 mb-1.5" for="">{$i18n.t('Current Password')}</label>
                    <input type="password" placeholder="••••••••" class="w-full px-3.5 py-2.5 rounded-xl border border-[#e2e8f0] dark:border-gray-700 bg-white dark:bg-gray-800 text-[#334155] dark:text-white outline-none" bind:value={currentPassword} autocomplete="current-password" required/>
                </div>
                <div class="mb-4 w-full">
                    <label class="block text-xs font-semibold text-[#5a6677] dark:text-gray-400 mb-1.5" for=" ">{$i18n.t('New Password')}</label>
                    <input type="password" placeholder="••••••••" class="w-full px-3.5 py-2.5 rounded-xl border border-[#e2e8f0] dark:border-gray-700 bg-white dark:bg-gray-800 text-[#334155] dark:text-white outline-none" bind:value={newPassword} autocomplete="new-password" required/>
                </div>
                <div class="mb-4 w-full md:col-span-2">
                    <label class="block text-xs font-semibold text-[#5a6677] dark:text-gray-400 mb-1.5" for="">{$i18n.t('Confirm Password')}</label>
                    <input type="password" placeholder="••••••••" class="w-full px-3.5 py-2.5 rounded-xl border border-[#e2e8f0] dark:border-gray-700 bg-white dark:bg-gray-800 text-[#334155] dark:text-white outline-none" bind:value={newPasswordConfirm} autocomplete="off" required/>
                </div>
            </div>
            <div>
                <button class="bg-[#3B82F6] text-white px-5 py-2.5 rounded-xl font-semibold border-none cursor-pointer mt-4 hover:bg-[#2563eb] transition-colors" on:click|stopPropagation={() => {updatePasswordHandler();}}>
                    {$i18n.t('Update password')}
                </button>
            </div>
        {/if}
    </section>

    <section class="flex flex-col md:flex-row items-start md:items-center gap-6 md:gap-[130px] p-6 bg-white dark:bg-gray-900 rounded-[1.2rem] border border-[#e2e8f0] dark:border-gray-800">
        <div class="flex flex-col gap-2 w-full md:w-auto">
            <label class="text-sm font-medium text-black dark:text-gray-200" for="theme">{$i18n.t('Theme')} :</label>
            <select id="theme" class="appearance-none bg-[#eef1f5] dark:bg-gray-800 border-none rounded-lg py-2.5 pl-3 pr-9 min-w-[220px] cursor-pointer outline-none dark:text-white custom-select-bg" bind:value={selectedTheme}
                on:change={() => themeChangeHandler(selectedTheme)}>
                    <option value="system">💻 {$i18n.t('System')}</option>
                    <option value="dark">🌑 {$i18n.t('Dark')}</option>
                    <option value="light">☀️ {$i18n.t('Light')}</option>
            </select>
        </div>

        <div class="flex flex-col gap-2 w-full md:w-auto">
            <label class="text-sm font-medium text-black dark:text-gray-200" for="language">{$i18n.t('Language')}:</label>
            <select id="language" class="appearance-none bg-[#eef1f5] dark:bg-gray-800 border-none rounded-lg py-2.5 pl-3 pr-9 min-w-[220px] cursor-pointer outline-none dark:text-white custom-select-bg" bind:value={lang}
                on:change={async () => {
                    $i18n.changeLanguage(lang);
                    localStorage.setItem('lang', lang);}}>
                {#each languages as l}
                    <option value={l.code}>{l.title}</option>
                {/each}
            </select>
        </div>
    </section>

    <footer class="mt-8 flex justify-end">
        <button class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-[40px] py-3 rounded-full font-semibold border-none cursor-pointer shadow-lg shadow-blue-500/20 transition-all active:scale-95" type="button" on:click={async () => {
                const res = await submitHandler();
                if (res) {
                    toast.success($i18n.t('Changes updated successfully'));
                    saveHandler();
                }
            }}>
            {$i18n.t('Save Changes')}
        </button>
    </footer>

</div>

<style>
    .custom-select-bg {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='18 15 12 9 6 15'%3E%3C/polyline%3E%3C/svg%3E"), 
                          url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%23666' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 12px top 35%, right 12px bottom 35%;
        background-size: 10px;
    }
</style>