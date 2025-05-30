import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.UnaryExpr;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.IfStmt;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.ast.stmt.ThrowStmt;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.NodeList;
public class BooleanAssertConverter extends ModifierVisitor<Void> {
    private boolean modified = false;

    @Override
    public MethodCallExpr visit(MethodCallExpr n, Void arg) {
        super.visit(n, arg);
        String methodName = n.getNameAsString();

        if ((methodName.equals("assertTrue") || methodName.equals("assertFalse")) && n.getArguments().size() == 1) {
            modified = true;
            convertToIfStmt(n, methodName);
        }
        return n;
    }

    private void convertToIfStmt(MethodCallExpr n, String methodName) {
        Expression argument = n.getArgument(0);
        Expression condition = argument.clone();

        // Determine if the argument is a simple boolean value or a comparison
        boolean isComparison = argument.isBinaryExpr();

        if (methodName.equals("assertTrue")) {
            // Negate the condition for assertTrue
            if (isComparison) {
                // If it's a comparison, invert the comparison operator
                BinaryExpr binaryExpr = argument.asBinaryExpr();
                BinaryExpr.Operator newOperator = invertOperator(binaryExpr.getOperator());
                condition = new BinaryExpr(binaryExpr.getLeft(), binaryExpr.getRight(), newOperator);
            } else {
                // Negate the condition if it's a simple value
                condition = new UnaryExpr(argument, UnaryExpr.Operator.LOGICAL_COMPLEMENT);
            }
        } else if (methodName.equals("assertFalse")) {
            // Use the condition as it is for assertFalse
            condition = argument;
        }

        IfStmt ifStmt = new IfStmt();
        ifStmt.setCondition(condition);

        // Create a copy of the original MethodCallExpr
        MethodCallExpr originalCall = n.clone();

        // Creating an ExpressionStmt with the original MethodCallExpr
        ExpressionStmt originalCallStmt = new ExpressionStmt(originalCall);

        // Set the then branch of the if statement to contain the original assertion call
        ifStmt.setThenStmt(new BlockStmt().addStatement(originalCallStmt));

        // Replace the parent ExpressionStmt with the new IfStmt
        if (n.findAncestor(ExpressionStmt.class).isPresent()) {
            ExpressionStmt parentStmt = n.findAncestor(ExpressionStmt.class).get();
            parentStmt.replace(ifStmt);
        }
    }

    private BinaryExpr.Operator invertOperator(BinaryExpr.Operator operator) {
        switch (operator) {
            case EQUALS:
                return BinaryExpr.Operator.NOT_EQUALS;
            case NOT_EQUALS:
                return BinaryExpr.Operator.EQUALS;
            case GREATER:
                return BinaryExpr.Operator.LESS_EQUALS;
            case LESS:
                return BinaryExpr.Operator.GREATER_EQUALS;
            case GREATER_EQUALS:
                return BinaryExpr.Operator.LESS;
            case LESS_EQUALS:
                return BinaryExpr.Operator.GREATER;
            default:
                return operator; // Default case should not happen for boolean comparisons
        }
    }

    public boolean isModified() {
        return modified;
    }
}
