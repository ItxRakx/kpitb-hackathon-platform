import Container from "@/components/ui/Container";
import Button from "@/components/ui/Button";

export default function NotFoundPage() {
  return (
    <section className="py-24">
      <Container size="sm" className="text-center">
        <div className="font-display text-7xl font-bold tracking-tight bg-gradient-to-r from-brand-600 to-accent-500 bg-clip-text text-transparent">
          404
        </div>
        <h1 className="mt-4 font-display text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
          Page not found
        </h1>
        <p className="mx-auto mt-4 max-w-md text-base text-slate-600">
          The page you are looking for doesn't exist or has been moved.
        </p>
        <div className="mt-8 inline-flex flex-wrap justify-center gap-3">
          <Button to="/">Back to Home</Button>
        </div>
      </Container>
    </section>
  );
}
