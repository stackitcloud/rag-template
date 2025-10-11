export interface AddressData {
  original: string;
  parcel?: string;
  gemarkung?: string;
  plan?: string;
  planStatus?: "available" | "none" | "unknown";
  festsetzungen?: string;
  lbo: string;
}

const lboFiles = [
  "/assets/LBO/LBO_2007-11-21.pdf",
  "/assets/LBO/LBO_2019-12-04.pdf",
  "/assets/LBO/LBO_2022-02-16.pdf",
  "/assets/LBO/LBO_2022-03-16.pdf",
  "/assets/LBO/LBO_2023-05-17.pdf",
  "/assets/LBO/LBO_2025-02-19.pdf",
];

const planFiles = [
  "/assets/bebauungsplan/bebauungsplan_10042113_013_0_Schinderwald_Armenberg.pdf",
  "/assets/bebauungsplan/bebauungsplan_10042113_047_0_Junkergelaende_Waldwieserstrasse.pdf",
  "/assets/bebauungsplan/bebauungsplan_10042113_082_0_Innenstadt_Merzig_Sued.pdf",
  "/assets/bebauungsplan/bebauungsplan_10042113_089_0_Suedkerntangente.pdf",
  "/assets/bebauungsplan/bebauungsplan-Soetern-In-der-Hohl-Satzung-2022-04-22-Plan.pdf",
  "/assets/bebauungsplan/bebauungsplan_10042113_013_0_Schinderwald_Armenberg-ocr.pdf",
];

const festsetzungenFiles = [
  "/assets/bebauungsplan/festsetzungen_10042113_013_0_Schinderwald_Armenberg.pdf",
  "/assets/bebauungsplan/festsetzungen_10042113_047_0_Junkergelaende_Waldwieserstrasse.pdf",
  "/assets/bebauungsplan/festsetzungen_10042113_082_0_Innenstadt_Merzig_Sued.pdf",
  "/assets/bebauungsplan/festsetzungen_10042113_089_0_Suedkerntangente.pdf",
];

export const addresses: AddressData[] = [
  { original: "Besseringen, Schinderwaldstraße 1", parcel: "1234/567", gemarkung: "Besseringen", plan: planFiles[0], planStatus: "available", festsetzungen: festsetzungenFiles[0], lbo: lboFiles[0] },
  { original: "Besseringen, Schinderwaldstraße 2", parcel: "1234/568", gemarkung: "Besseringen", plan: planFiles[0], planStatus: "available", festsetzungen: festsetzungenFiles[0], lbo: lboFiles[0] },
  { original: "Besseringen, Schinderwaldstraße 3", parcel: "1234/569", gemarkung: "Besseringen", plan: planFiles[0], planStatus: "available", festsetzungen: festsetzungenFiles[0], lbo: lboFiles[0] },
  { original: "Saarbrücken, Waldwieserstraße 10", parcel: "2345/678", gemarkung: "Saarbrücken", plan: planFiles[1], planStatus: "available", festsetzungen: festsetzungenFiles[1], lbo: lboFiles[1] },
  { original: "Saarbrücken, Waldwieserstraße 11", parcel: "2345/679", gemarkung: "Saarbrücken", plan: planFiles[1], planStatus: "available", festsetzungen: festsetzungenFiles[1], lbo: lboFiles[1] },
  { original: "Saarbrücken, Waldwieserstraße 12", parcel: "2345/680", gemarkung: "Saarbrücken", plan: planFiles[1], planStatus: "available", festsetzungen: festsetzungenFiles[1], lbo: lboFiles[1] },
  { original: "Saarlouis, Markt 5", parcel: "3456/789", gemarkung: "Saarlouis", planStatus: "none", lbo: lboFiles[5] },
  { original: "Saarlouis, Markt 6", parcel: "3456/790", gemarkung: "Saarlouis", planStatus: "none", lbo: lboFiles[5] },
  { original: "Saarlouis, Markt 7", parcel: "3456/791", gemarkung: "Saarlouis", planStatus: "none", lbo: lboFiles[5] },
  { original: "Merzig, Innenstadt Süd 15", parcel: "4567/890", gemarkung: "Merzig", plan: planFiles[2], planStatus: "available", festsetzungen: festsetzungenFiles[2], lbo: lboFiles[3] },
  { original: "Merzig, Innenstadt Süd 16", parcel: "4567/891", gemarkung: "Merzig", plan: planFiles[2], planStatus: "available", festsetzungen: festsetzungenFiles[2], lbo: lboFiles[3] },
  { original: "Merzig, Innenstadt Süd 17", parcel: "4567/892", gemarkung: "Merzig", plan: planFiles[2], planStatus: "available", festsetzungen: festsetzungenFiles[2], lbo: lboFiles[3] },
  { original: "Homburg, Universitätsstraße 20", parcel: "5678/901", gemarkung: "Homburg", planStatus: "none", lbo: lboFiles[5] },
  { original: "Homburg, Universitätsstraße 21", parcel: "5678/902", gemarkung: "Homburg", planStatus: "none", lbo: lboFiles[5] },
  { original: "Homburg, Universitätsstraße 22", parcel: "5678/903", gemarkung: "Homburg", planStatus: "none", lbo: lboFiles[5] },
  { original: "Saarbrücken, Südkern Tangente 3", parcel: "6789/012", gemarkung: "Saarbrücken", plan: planFiles[3], planStatus: "available", festsetzungen: festsetzungenFiles[3], lbo: lboFiles[5] },
  { original: "Saarbrücken, Südkern Tangente 4", parcel: "6789/013", gemarkung: "Saarbrücken", plan: planFiles[3], planStatus: "available", festsetzungen: festsetzungenFiles[3], lbo: lboFiles[5] },
  { original: "Saarbrücken, Südkern Tangente 5", parcel: "6789/014", gemarkung: "Saarbrücken", plan: planFiles[3], planStatus: "available", festsetzungen: festsetzungenFiles[3], lbo: lboFiles[5] },
  { original: "St. Wendel, Schlossstraße 7", parcel: "7890/123", gemarkung: "St. Wendel", planStatus: "unknown", lbo: lboFiles[0] },
  { original: "St. Wendel, Schlossstraße 8", parcel: "7890/124", gemarkung: "St. Wendel", planStatus: "unknown", lbo: lboFiles[0] },
  { original: "St. Wendel, Schlossstraße 9", parcel: "7890/125", gemarkung: "St. Wendel", planStatus: "unknown", lbo: lboFiles[0] },
  { original: "Nohfelden, In der Hohl 12", parcel: "8901/234", gemarkung: "Nohfelden", plan: planFiles[4], planStatus: "available", lbo: lboFiles[1] },
  { original: "Nohfelden, In der Hohl 13", parcel: "8901/235", gemarkung: "Nohfelden", plan: planFiles[4], planStatus: "available", lbo: lboFiles[1] },
  { original: "Nohfelden, In der Hohl 14", parcel: "8901/236", gemarkung: "Nohfelden", plan: planFiles[4], planStatus: "available", lbo: lboFiles[1] },
  { original: "Dillingen, Dillinger Straße 25", parcel: "9012/345", gemarkung: "Dillingen", planStatus: "unknown", lbo: lboFiles[2] },
  { original: "Dillingen, Dillinger Straße 26", parcel: "9012/346", gemarkung: "Dillingen", planStatus: "unknown", lbo: lboFiles[2] },
  { original: "Dillingen, Dillinger Straße 27", parcel: "9012/347", gemarkung: "Dillingen", planStatus: "unknown", lbo: lboFiles[2] },
  { original: "Besseringen, Armenberg 8", parcel: "0123/456", gemarkung: "Besseringen", plan: planFiles[5], planStatus: "available", festsetzungen: festsetzungenFiles[0], lbo: lboFiles[3] },
  { original: "Besseringen, Armenberg 9", parcel: "0123/457", gemarkung: "Besseringen", plan: planFiles[5], planStatus: "available", festsetzungen: festsetzungenFiles[0], lbo: lboFiles[3] },
  { original: "Besseringen, Armenberg 10", parcel: "0123/458", gemarkung: "Besseringen", plan: planFiles[5], planStatus: "available", festsetzungen: festsetzungenFiles[0], lbo: lboFiles[3] },
];

export function searchAddresses(query: string): AddressData[] {
  const lowerQuery = query.toLowerCase();
  return addresses.filter(
    (addr) =>
      addr.original.toLowerCase().includes(lowerQuery) ||
      (addr.parcel && addr.parcel.toLowerCase().includes(lowerQuery))
  );
}
