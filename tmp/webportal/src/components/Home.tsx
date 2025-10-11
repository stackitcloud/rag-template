import { Component, createSignal } from 'solid-js';
import { useNavigate } from '@solidjs/router';

const Home: Component = () => {
	const navigate = useNavigate();
	const [address, setAddress] = createSignal('');

	const handleSubmit = (e: Event) => {
		e.preventDefault();
		if (address().trim()) {
			navigate(`/address?q=${encodeURIComponent(address())}`);
		}
	};

	return (
		<div class="min-h-screen bg-gray-50 flex items-center justify-center">
			<div class="max-w-md w-full bg-white shadow-lg rounded-lg p-8">
				<h1 class="text-2xl font-bold text-gray-900 mb-4 text-center">Informationsportal der Unteren Bauaufsichtsbehörden des Saarlandes</h1>
				<p class="text-gray-600 mb-6 text-center">Geben Sie eine Adresse oder Flurstücknummer ein, um relevante Bauvorschriften und Bebauungspläne abzurufen und Fragen zu stellen.</p>
				<form onSubmit={handleSubmit} class="space-y-4">
					<div>
						<label for="address" class="block text-sm font-medium text-gray-700 mb-2">Adresse oder Flurstücknummer eingeben:</label>
						<input
							type="text"
							id="address"
							value={address()}
							onInput={(e) => setAddress(e.currentTarget.value)}
							placeholder="z.B. Saarbrücken, Markt 1 oder 1234/567"
							class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
							required
						/>
					</div>
					<button type="submit" class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
						Adresse prüfen
					</button>
				</form>
			</div>
		</div>
	);
};

export default Home;