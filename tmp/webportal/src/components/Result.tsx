import { Component, createEffect, createSignal, For } from 'solid-js';
import { useSearchParams } from '@solidjs/router';
import { addresses, type AddressData } from '../lib/data';

const Result: Component = () => {
	const [searchParams] = useSearchParams();
	const [addr, setAddr] = createSignal('');
	const [data, setData] = createSignal<AddressData | undefined>();
	const [messages, setMessages] = createSignal<string[]>([]);
	const [input, setInput] = createSignal('');

	createEffect(() => {
		const a = searchParams.addr || '';
		setAddr(a);
		setData(addresses.find(ad => ad.original === a));
	});

	const handleChatSubmit = (e: Event) => {
		e.preventDefault();
		if (input().trim() && data()) {
			let prompt = `Prompt: ${input()}\n\nLBO Document: ${data()!.lbo}`;
			if (data()!.plan) {
				prompt += `\n\nBebauungsplan Document: ${data()!.plan}`;
			}
			if (data()!.festsetzungen) {
				prompt += `\n\nFestsetzungen Document: ${data()!.festsetzungen}`;
			}
			setMessages(prev => [...prev, prompt]);
			setInput('');
		}
	};

	return (
		<div class="min-h-screen bg-gray-50 py-8">
			<div class="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-8">
				{data() ? (
					<>
						<h1 class="text-2xl font-bold text-gray-900 mb-4">Dokumente und Informationen für: {data()!.original}</h1>
						{(data()!.parcel || data()!.gemarkung) && (
							<p class="text-gray-700 mb-4">
								{data()!.gemarkung && `Gemarkung: ${data()!.gemarkung}`}
								{data()!.parcel && data()!.gemarkung && ' | '}
								{data()!.parcel && `Flurstücknummer: ${data()!.parcel}`}
							</p>
						)}
						<div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
							<div>
								<h2 class="text-lg font-semibold text-gray-800 mb-2">Bebauungsplan:</h2>
								{data()!.planStatus === 'available' ? (
									<div class="space-y-2">
										<a href={data()!.plan!} download class="inline-block bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">Download Bebauungsplan PDF</a>
										{data()!.festsetzungen && (
											<a href={data()!.festsetzungen} download class="inline-block bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors ml-2">Download Festsetzungen PDF</a>
										)}
									</div>
								) : data()!.planStatus === 'none' ? (
									<p class="text-gray-600">Kein Bebauungsplan vorhanden</p>
								) : (
									<p class="text-gray-600">Status unbekannt</p>
								)}
							</div>
							<div>
								<h2 class="text-lg font-semibold text-gray-800 mb-2">Landesbauordnung:</h2>
								{(() => {
									const lboPath = data()!.lbo;
									const dateMatch = lboPath.match(/LBO_(\d{4}-\d{2}-\d{2})\.pdf$/);
									const dateStr = dateMatch ? dateMatch[1] : '';
									const formattedDate = dateStr ? new Date(dateStr).toLocaleDateString('de-DE', { day: '2-digit', month: 'long', year: 'numeric' }) : '';
									return (
										<a href={lboPath} download class="inline-block bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors">
											Download LBO vom {formattedDate}
										</a>
									);
								})()}
							</div>
						</div>
						<div class="border-t pt-6">
							<h2 class="text-xl font-bold text-gray-900 mb-2">Chatbot für Baufragen</h2>
							<p class="text-gray-600 mb-4">Stellen Sie Fragen zu den Bauvorschriften und Bebauungsplänen. Der Chatbot nutzt die Inhalte der oben genannten Dokumente, um Ihnen zu helfen.</p>
							<div class="bg-gray-100 p-4 rounded-md mb-4 max-h-64 overflow-y-auto">
								<For each={messages()}>
									{(msg) => <p class="text-gray-800 mb-2 whitespace-pre-line">{msg}</p>}
								</For>
							</div>
							<form onSubmit={handleChatSubmit} class="flex space-x-2">
								<input
									type="text"
									value={input()}
									onInput={(e) => setInput(e.currentTarget.value)}
									placeholder="z.B. Welche Bauhöhe ist erlaubt?"
									class="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
									required
								/>
								<button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">
									Frage senden
								</button>
							</form>
						</div>
						<div class="mt-6">
							<a href="/" class="text-blue-600 hover:text-blue-800 underline">Zurück zur Suche</a>
						</div>
					</>
				) : (
					<>
						<p class="text-red-600 mb-4">Adresse nicht gefunden. Bitte versuchen Sie es erneut.</p>
						<a href="/" class="text-blue-600 hover:text-blue-800 underline">Zurück zur Suche</a>
					</>
				)}
			</div>
		</div>
	);
};

export default Result;