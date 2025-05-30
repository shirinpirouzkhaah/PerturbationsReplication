import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.StringLiteralExpr;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.stmt.AssertStmt;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.IfStmt;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.ast.stmt.ThrowStmt;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.NodeList;

public class NotNullAssertConverter extends ModifierVisitor<Void> {
    private boolean modified = false;

    @Override
    public MethodCallExpr visit(MethodCallExpr n, Void arg) {
        super.visit(n, arg);
        String methodName = n.getNameAsString();

        // Handle specific not-null check methods
        if (methodName.equals("assertNotNull") || methodName.equals("notNull") ||
                methodName.equals("requireNonNull") || methodName.equals("checkNotNullParam")) {
            modified = true;
            convertToIfStmt(n);
        }

        // Handle specific null-check methods
        if (methodName.equals("assertNull")) {
            modified = true;
            convertToIfStmtnull(n);
        }

        return n;
    }

    @Override
    public AssertStmt visit(AssertStmt n, Void arg) {
        super.visit(n, arg);

        Expression check = n.getCheck();

        if (check.isBinaryExpr()) {
            BinaryExpr binary = check.asBinaryExpr();
            Expression left = binary.getLeft();
            Expression right = binary.getRight();
            BinaryExpr.Operator op = binary.getOperator();

            boolean isNullCheck = (right.isNullLiteralExpr() || left.isNullLiteralExpr()) &&
                    (op == BinaryExpr.Operator.EQUALS || op == BinaryExpr.Operator.NOT_EQUALS);

            if (isNullCheck) {
                modified = true;

                // Flip the condition: if (x != null) when assert x == null
                BinaryExpr flippedCondition = new BinaryExpr(left, right,
                        (op == BinaryExpr.Operator.EQUALS) ? BinaryExpr.Operator.NOT_EQUALS : BinaryExpr.Operator.EQUALS);

                IfStmt ifStmt = new IfStmt();
                ifStmt.setCondition(flippedCondition);

                Expression message = n.getMessage().orElse(new StringLiteralExpr("Null assertion failed"));

                ThrowStmt throwStmt = new ThrowStmt(new com.github.javaparser.ast.expr.ObjectCreationExpr(
                        null,
                        new ClassOrInterfaceType(null, "AssertionError"),
                        NodeList.nodeList(message)
                ));

                ifStmt.setThenStmt(new BlockStmt().addStatement(throwStmt));

                n.replace(ifStmt);
            }
        }

        return n;
    }

    private void convertToIfStmtnull(MethodCallExpr n) {
        Expression arg = n.getArgument(0);

        BinaryExpr condition = new BinaryExpr(
                arg,
                new com.github.javaparser.ast.expr.NullLiteralExpr(),
                BinaryExpr.Operator.NOT_EQUALS
        );

        IfStmt ifStmt = new IfStmt();
        ifStmt.setCondition(condition);

        // Create a copy of the original MethodCallExpr
        MethodCallExpr originalCall = n.clone();

        // Creating an ExpressionStmt with the original MethodCallExpr
        ExpressionStmt originalCallStmt = new ExpressionStmt(originalCall);

        // Set the then branch of the if statement to contain the original assertion call
        ifStmt.setThenStmt(new BlockStmt().addStatement(originalCallStmt));

        // Replace the parent ExpressionStmt with the new IfStmt
        n.findAncestor(ExpressionStmt.class).ifPresent(parentStmt -> parentStmt.replace(ifStmt));
    }

    private void convertToIfStmt(MethodCallExpr n) {
        int valueIndex = 0; // Default index for value
        int messageIndex = 1; // Default index for message

        if (n.getNameAsString().equals("checkNotNullParam")) {
            // checkNotNullParam has a reversed parameter order
            valueIndex = 1;
            messageIndex = 0;
        }

        BinaryExpr condition = new BinaryExpr(
                n.getArgument(valueIndex),
                new com.github.javaparser.ast.expr.NullLiteralExpr(),
                BinaryExpr.Operator.EQUALS
        );

        IfStmt ifStmt = new IfStmt();
        ifStmt.setCondition(condition);

        // Create a copy of the original MethodCallExpr
        MethodCallExpr originalCall = n.clone();

        // Creating an ExpressionStmt with the original MethodCallExpr
        ExpressionStmt originalCallStmt = new ExpressionStmt(originalCall);

        // Set the then branch of the if statement to contain the original assertion call
        ifStmt.setThenStmt(new BlockStmt().addStatement(originalCallStmt));

        // Replace the parent ExpressionStmt with the new IfStmt
        n.findAncestor(ExpressionStmt.class).ifPresent(parentStmt -> parentStmt.replace(ifStmt));
    }

    public boolean isModified() {
        return modified;
    }
}
