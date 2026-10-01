import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Realistic Video Generator',
  description: 'Railway-ready AI video generation starter',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
