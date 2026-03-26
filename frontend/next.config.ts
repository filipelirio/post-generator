import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  /* config options here */
  images: {
    domains: ["localhost"], // Para imagens locais ou do WP se precisar
  },
};

export default nextConfig;
