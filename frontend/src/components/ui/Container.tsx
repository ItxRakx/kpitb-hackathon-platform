import type { ReactNode, HTMLAttributes } from "react";

type Props = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
  size?: "sm" | "md" | "lg";
};

const sizes = {
  sm: "max-w-4xl",
  md: "max-w-6xl",
  lg: "max-w-7xl",
};

export default function Container({ children, size = "lg", className = "", ...rest }: Props) {
  return (
    <div className={`mx-auto w-full px-4 sm:px-6 lg:px-8 ${sizes[size]} ${className}`} {...rest}>
      {children}
    </div>
  );
}
