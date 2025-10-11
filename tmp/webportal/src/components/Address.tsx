import { Component, createEffect, createSignal } from 'solid-js';
import { useNavigate, useSearchParams } from '@solidjs/router';
import { searchAddresses, type AddressData } from '../lib/data';

const Address: Component = () => {
	const navigate = useNavigate();
	const [searchParams] = useSearchParams();
	const [query, setQuery] = createSignal('');
	const [matches, setMatches] = createSignal<AddressData[]>([]);

	createEffect(() => {
		const q = searchParams.q || '';
		setQuery(q);
		setMatches(searchAddresses(q));
	});

	const selectAddress = (addr: string) => {
		navigate(`/result?addr=${encodeURIComponent(addr)}`);
	};

	return (
		<div class="min-h-screen bg-gray-50 py-8">
			<div class="max-w-2xl mx-auto bg-white shadow-lg rounded-lg p-8">
				{matches().length === 0 ? (
					<>
						<p class="text-red-600 mb-4">Keine passende Adresse gefunden für "{query()}". Bitte überprüfen Sie die Eingabe oder versuchen Sie eine andere Adresse.</p>
						<a href="/" class="text-blue-600 hover:text-blue-800 underline">Zurück zur Suche</a>
					</>
				) : matches().length === 1 ? (
					<>
						{/* Redirect */}
						{(() => {
							navigate(`/result?addr=${encodeURIComponent(matches()[0].original)}`);
							return null;
						})()}
					</>
				) : (
					<>
						<h1 class="text-2xl font-bold text-gray-900 mb-4">Mögliche Adressen oder Flurstücke für: {query()}</h1>
						<p class="text-gray-600 mb-6">Wählen Sie die passende Adresse aus, um die relevanten Dokumente und den Chatbot zu öffnen.</p>
						<ul class="space-y-2 mb-6">
							{matches().map((match) => (
								<li>
									<button
										onClick={() => selectAddress(match.original)}
										class="w-full text-left px-4 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-md transition-colors"
									>
										{match.original}
									</button>
								</li>
							))}
						</ul>
						<a href="/" class="text-blue-600 hover:text-blue-800 underline">Zurück zur Suche</a>
					</>
				)}
			</div>
		</div>
	);
};

export default Address;