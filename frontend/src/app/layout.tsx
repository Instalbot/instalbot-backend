import type { Metadata } from 'next'
import {Montserrat} from 'next/font/google'
import Navbar from "@/app/navbar/navbar";

import './globals.css'

const montserrat = Montserrat({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Instalbot',
  description: 'A solution for Instaling grades',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={montserrat.className}>
        <nav>
          <Navbar />
        </nav>
        {children}
      </body>
    </html>
  )
}
