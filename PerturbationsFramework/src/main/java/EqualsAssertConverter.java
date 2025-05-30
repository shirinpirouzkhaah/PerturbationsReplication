import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.expr.BinaryExpr;
import com.github.javaparser.ast.expr.Expression;
import com.github.javaparser.ast.expr.MethodCallExpr;
import com.github.javaparser.ast.expr.StringLiteralExpr;
import com.github.javaparser.ast.type.ClassOrInterfaceType;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.ExpressionStmt;
import com.github.javaparser.ast.stmt.IfStmt;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.ast.stmt.ThrowStmt;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.NodeList;

public class EqualsAssertConverter extends ModifierVisitor<Void> {
    private boolean modified = false;

    @Override
    public MethodCallExpr visit(MethodCallExpr n, Void arg) {
        super.visit(n, arg);
        String methodName = n.getNameAsString();

        if ((methodName.equals("assertEquals") || methodName.equals("assertArrayEquals") || methodName.equals("assertSame") || methodName.equals("assertNotEquals")) && n.getArguments().size() == 2) {
            modified = true;
            convertToIfStmt(n, methodName);
        }
        return n;
    }

    private void convertToIfStmt(MethodCallExpr n, String methodName) {
        Expression firstArgument = n.getArgument(0);
        Expression secondArgument = n.getArgument(1);

        BinaryExpr.Operator operator = methodName.equals("assertNotEquals") ?
                BinaryExpr.Operator.EQUALS : BinaryExpr.Operator.NOT_EQUALS;

        BinaryExpr condition = new BinaryExpr(firstArgument, secondArgument, operator);

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

    public boolean isModified() {
        return modified;
    }
}
