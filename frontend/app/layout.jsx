import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata = {
  title: "IT Support Dashboard",
  description: "Ticket management dashboard for IT Support",
};

// Without this, mobile browsers assume a desktop-width layout and zoom the
// whole page out to fit — this is what makes it render at the correct
// actual size on phones instead of needing a manual pinch-to-fix.
export const viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}