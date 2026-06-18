fn greet(name: &str) -> String {
    format!("cog:{name}")
}

fn main() {
    println!("{}", greet("world"));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greet() {
        assert_eq!(greet("x"), "cog:x");
    }
}
