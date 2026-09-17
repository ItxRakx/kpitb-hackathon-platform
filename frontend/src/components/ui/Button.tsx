import type { ReactNode, ButtonHTMLAttributes, AnchorHTMLAttributes } from "react";
import { Link } from "react-router-dom";

type Variant = "primary" | "secondary" | "ghost";
type Size = "sm" | "md" | "lg";

const variantClass: Record<Variant, string> = {
  primary: "btn-primary",
  secondary: "btn-secondary",
  ghost: "btn-ghost",
};

const sizeClass: Record<Size, string> = {
  sm: "!px-3.5 !py-1.5 text-xs",
  md: "",
  lg: "!px-6 !py-3 text-base",
};

type BaseProps = {
  variant?: Variant;
  size?: Size;
  children: ReactNode;
  className?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
};

type ButtonProps = BaseProps &
  ButtonHTMLAttributes<HTMLButtonElement> & {
    to?: never;
    href?: never;
  };

type LinkProps = BaseProps & {
  to: string;
  href?: never;
  onClick?: () => void;
  className?: string;
};

type AnchorProps = BaseProps &
  AnchorHTMLAttributes<HTMLAnchorElement> & {
    href: string;
    to?: never;
  };

type Props = ButtonProps | LinkProps | AnchorProps;

export default function Button(props: Props) {
  const { variant = "primary", size = "md", className = "", leftIcon, rightIcon, children } = props;
  const classes = `${variantClass[variant]} ${sizeClass[size]} ${className}`.trim();

  const content = (
    <>
      {leftIcon ? <span className="-ml-1">{leftIcon}</span> : null}
      <span>{children}</span>
      {rightIcon ? <span className="-mr-1">{rightIcon}</span> : null}
    </>
  );

  if ("to" in props && props.to) {
    const {
      variant: _v, size: _s, leftIcon: _l, rightIcon: _r,
      children: _c, className: _cn, to: _t, href: _h, ...rest
    } = props as LinkProps & { href?: never };
    void _v; void _s; void _l; void _r; void _c; void _cn; void _t; void _h;
    return (
      <Link to={props.to} className={classes} {...rest}>
        {content}
      </Link>
    );
  }

  if ("href" in props && props.href) {
    const {
      variant: _v, size: _s, leftIcon: _l, rightIcon: _r,
      children: _c, className: _cn, href: _h, to: _t, ...rest
    } = props as AnchorProps & { to?: never };
    void _v; void _s; void _l; void _r; void _c; void _cn; void _h; void _t;
    return (
      <a className={classes} href={props.href} {...rest}>
        {content}
      </a>
    );
  }

  const {
    variant: _v, size: _s, leftIcon: _l, rightIcon: _r,
    children: _c, className: _cn, to: _t, href: _h, ...rest
  } = props as ButtonProps;
  void _v; void _s; void _l; void _r; void _c; void _cn; void _t; void _h;
  return (
    <button className={classes} {...rest}>
      {content}
    </button>
  );
}
