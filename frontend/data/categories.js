import { Mail, Wifi, HardDrive, AppWindow, CircleHelp } from "lucide-react";

export const CATEGORIES = [
  { key: "email", label: "Email Issue", icon: Mail },
  { key: "network", label: "Network Issue", icon: Wifi },
  { key: "hardware", label: "Hardware Issue", icon: HardDrive },
  { key: "software", label: "Software Issue", icon: AppWindow },
  { key: "other", label: "Other", icon: CircleHelp },
];

export function getCategory(key) {
  return CATEGORIES.find((c) => c.key === key) ?? CATEGORIES[CATEGORIES.length - 1];
}
