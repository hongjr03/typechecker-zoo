use system_f_omega::typecheck_module_silent;

/// Test that type mismatches are caught
#[test]
fn test_type_error() {
    let source = r#"
        wrong :: Unit;
        wrong = 42;
    "#;

    assert!(typecheck_module_silent(source, "test.hs").is_err());
}

/// Test that existential variables are properly "zonked" (resolved) when
/// checking subtyping. The else branch returns Bool (from <) but the function
/// is declared to return Int.
#[test]
fn test_if_branch_type_mismatch() {
    let source = r#"
        bad :: Int -> Int;
        bad n = if n <= 1 then n else (bad (n - 1)) < (bad (n - 2));
    "#;

    assert!(typecheck_module_silent(source, "test.hs").is_err());
}

/// Test that missing type signatures are rejected
#[test]
fn test_missing_type_signature() {
    let source = r#"
        mystery = 1 + 1;
    "#;

    assert!(typecheck_module_silent(source, "test.hs").is_err());
}
