// Generated from /Applications/XAMPP/xamppfiles/htdocs/rdbms/src/parser/SQL.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.Lexer;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.TokenStream;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.misc.*;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast", "CheckReturnValue", "this-escape"})
public class SQLLexer extends Lexer {
	static { RuntimeMetaData.checkVersion("4.13.1", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		T__0=1, T__1=2, T__2=3, T__3=4, T__4=5, T__5=6, T__6=7, T__7=8, TCNAME=9, 
		SELECT=10, FROM=11, WHERE=12, AND=13, OR=14, SEMICOLON=15, DELETE=16, 
		INSERT=17, INTO=18, VALUES=19, NULL=20, DOT=21, OPENPAR=22, CLOSEPAR=23, 
		WORD=24, NUMBER=25, STRING=26, WS=27;
	public static String[] channelNames = {
		"DEFAULT_TOKEN_CHANNEL", "HIDDEN"
	};

	public static String[] modeNames = {
		"DEFAULT_MODE"
	};

	private static String[] makeRuleNames() {
		return new String[] {
			"T__0", "T__1", "T__2", "T__3", "T__4", "T__5", "T__6", "T__7", "TCNAME", 
			"SELECT", "FROM", "WHERE", "AND", "OR", "SEMICOLON", "DELETE", "INSERT", 
			"INTO", "VALUES", "NULL", "DOT", "OPENPAR", "CLOSEPAR", "WORD", "NUMBER", 
			"STRING", "WS"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "','", "'*'", "'='", "'<>'", "'<'", "'>'", "'<='", "'>='", null, 
			"'select'", "'from'", "'where'", "'and'", "'or'", "';'", "'delete'", 
			"'insert'", "'into'", "'values'", "'null'", "'.'", "'('", "')'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, null, null, null, null, null, null, null, null, "TCNAME", "SELECT", 
			"FROM", "WHERE", "AND", "OR", "SEMICOLON", "DELETE", "INSERT", "INTO", 
			"VALUES", "NULL", "DOT", "OPENPAR", "CLOSEPAR", "WORD", "NUMBER", "STRING", 
			"WS"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}


	public SQLLexer(CharStream input) {
		super(input);
		_interp = new LexerATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	@Override
	public String getGrammarFileName() { return "SQL.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public String[] getChannelNames() { return channelNames; }

	@Override
	public String[] getModeNames() { return modeNames; }

	@Override
	public ATN getATN() { return _ATN; }

	public static final String _serializedATN =
		"\u0004\u0000\u001b\u00b2\u0006\uffff\uffff\u0002\u0000\u0007\u0000\u0002"+
		"\u0001\u0007\u0001\u0002\u0002\u0007\u0002\u0002\u0003\u0007\u0003\u0002"+
		"\u0004\u0007\u0004\u0002\u0005\u0007\u0005\u0002\u0006\u0007\u0006\u0002"+
		"\u0007\u0007\u0007\u0002\b\u0007\b\u0002\t\u0007\t\u0002\n\u0007\n\u0002"+
		"\u000b\u0007\u000b\u0002\f\u0007\f\u0002\r\u0007\r\u0002\u000e\u0007\u000e"+
		"\u0002\u000f\u0007\u000f\u0002\u0010\u0007\u0010\u0002\u0011\u0007\u0011"+
		"\u0002\u0012\u0007\u0012\u0002\u0013\u0007\u0013\u0002\u0014\u0007\u0014"+
		"\u0002\u0015\u0007\u0015\u0002\u0016\u0007\u0016\u0002\u0017\u0007\u0017"+
		"\u0002\u0018\u0007\u0018\u0002\u0019\u0007\u0019\u0002\u001a\u0007\u001a"+
		"\u0001\u0000\u0001\u0000\u0001\u0001\u0001\u0001\u0001\u0002\u0001\u0002"+
		"\u0001\u0003\u0001\u0003\u0001\u0003\u0001\u0004\u0001\u0004\u0001\u0005"+
		"\u0001\u0005\u0001\u0006\u0001\u0006\u0001\u0006\u0001\u0007\u0001\u0007"+
		"\u0001\u0007\u0001\b\u0001\b\u0001\b\u0001\b\u0004\bO\b\b\u000b\b\f\b"+
		"P\u0001\t\u0001\t\u0001\t\u0001\t\u0001\t\u0001\t\u0001\t\u0001\n\u0001"+
		"\n\u0001\n\u0001\n\u0001\n\u0001\u000b\u0001\u000b\u0001\u000b\u0001\u000b"+
		"\u0001\u000b\u0001\u000b\u0001\f\u0001\f\u0001\f\u0001\f\u0001\r\u0001"+
		"\r\u0001\r\u0001\u000e\u0001\u000e\u0001\u000f\u0001\u000f\u0001\u000f"+
		"\u0001\u000f\u0001\u000f\u0001\u000f\u0001\u000f\u0001\u0010\u0001\u0010"+
		"\u0001\u0010\u0001\u0010\u0001\u0010\u0001\u0010\u0001\u0010\u0001\u0011"+
		"\u0001\u0011\u0001\u0011\u0001\u0011\u0001\u0011\u0001\u0012\u0001\u0012"+
		"\u0001\u0012\u0001\u0012\u0001\u0012\u0001\u0012\u0001\u0012\u0001\u0013"+
		"\u0001\u0013\u0001\u0013\u0001\u0013\u0001\u0013\u0001\u0014\u0001\u0014"+
		"\u0001\u0015\u0001\u0015\u0001\u0016\u0001\u0016\u0001\u0017\u0004\u0017"+
		"\u0094\b\u0017\u000b\u0017\f\u0017\u0095\u0001\u0017\u0005\u0017\u0099"+
		"\b\u0017\n\u0017\f\u0017\u009c\t\u0017\u0001\u0018\u0004\u0018\u009f\b"+
		"\u0018\u000b\u0018\f\u0018\u00a0\u0001\u0019\u0001\u0019\u0005\u0019\u00a5"+
		"\b\u0019\n\u0019\f\u0019\u00a8\t\u0019\u0001\u0019\u0001\u0019\u0001\u001a"+
		"\u0004\u001a\u00ad\b\u001a\u000b\u001a\f\u001a\u00ae\u0001\u001a\u0001"+
		"\u001a\u0001\u00a6\u0000\u001b\u0001\u0001\u0003\u0002\u0005\u0003\u0007"+
		"\u0004\t\u0005\u000b\u0006\r\u0007\u000f\b\u0011\t\u0013\n\u0015\u000b"+
		"\u0017\f\u0019\r\u001b\u000e\u001d\u000f\u001f\u0010!\u0011#\u0012%\u0013"+
		"\'\u0014)\u0015+\u0016-\u0017/\u00181\u00193\u001a5\u001b\u0001\u0000"+
		"\u0014\u0002\u0000SSss\u0002\u0000EEee\u0002\u0000LLll\u0002\u0000CCc"+
		"c\u0002\u0000TTtt\u0002\u0000FFff\u0002\u0000RRrr\u0002\u0000OOoo\u0002"+
		"\u0000MMmm\u0002\u0000WWww\u0002\u0000HHhh\u0002\u0000AAaa\u0002\u0000"+
		"NNnn\u0002\u0000DDdd\u0002\u0000IIii\u0002\u0000VVvv\u0002\u0000UUuu\u0003"+
		"\u0000AZ__az\u0001\u000009\u0003\u0000\t\n\r\r  \u00b7\u0000\u0001\u0001"+
		"\u0000\u0000\u0000\u0000\u0003\u0001\u0000\u0000\u0000\u0000\u0005\u0001"+
		"\u0000\u0000\u0000\u0000\u0007\u0001\u0000\u0000\u0000\u0000\t\u0001\u0000"+
		"\u0000\u0000\u0000\u000b\u0001\u0000\u0000\u0000\u0000\r\u0001\u0000\u0000"+
		"\u0000\u0000\u000f\u0001\u0000\u0000\u0000\u0000\u0011\u0001\u0000\u0000"+
		"\u0000\u0000\u0013\u0001\u0000\u0000\u0000\u0000\u0015\u0001\u0000\u0000"+
		"\u0000\u0000\u0017\u0001\u0000\u0000\u0000\u0000\u0019\u0001\u0000\u0000"+
		"\u0000\u0000\u001b\u0001\u0000\u0000\u0000\u0000\u001d\u0001\u0000\u0000"+
		"\u0000\u0000\u001f\u0001\u0000\u0000\u0000\u0000!\u0001\u0000\u0000\u0000"+
		"\u0000#\u0001\u0000\u0000\u0000\u0000%\u0001\u0000\u0000\u0000\u0000\'"+
		"\u0001\u0000\u0000\u0000\u0000)\u0001\u0000\u0000\u0000\u0000+\u0001\u0000"+
		"\u0000\u0000\u0000-\u0001\u0000\u0000\u0000\u0000/\u0001\u0000\u0000\u0000"+
		"\u00001\u0001\u0000\u0000\u0000\u00003\u0001\u0000\u0000\u0000\u00005"+
		"\u0001\u0000\u0000\u0000\u00017\u0001\u0000\u0000\u0000\u00039\u0001\u0000"+
		"\u0000\u0000\u0005;\u0001\u0000\u0000\u0000\u0007=\u0001\u0000\u0000\u0000"+
		"\t@\u0001\u0000\u0000\u0000\u000bB\u0001\u0000\u0000\u0000\rD\u0001\u0000"+
		"\u0000\u0000\u000fG\u0001\u0000\u0000\u0000\u0011J\u0001\u0000\u0000\u0000"+
		"\u0013R\u0001\u0000\u0000\u0000\u0015Y\u0001\u0000\u0000\u0000\u0017^"+
		"\u0001\u0000\u0000\u0000\u0019d\u0001\u0000\u0000\u0000\u001bh\u0001\u0000"+
		"\u0000\u0000\u001dk\u0001\u0000\u0000\u0000\u001fm\u0001\u0000\u0000\u0000"+
		"!t\u0001\u0000\u0000\u0000#{\u0001\u0000\u0000\u0000%\u0080\u0001\u0000"+
		"\u0000\u0000\'\u0087\u0001\u0000\u0000\u0000)\u008c\u0001\u0000\u0000"+
		"\u0000+\u008e\u0001\u0000\u0000\u0000-\u0090\u0001\u0000\u0000\u0000/"+
		"\u0093\u0001\u0000\u0000\u00001\u009e\u0001\u0000\u0000\u00003\u00a2\u0001"+
		"\u0000\u0000\u00005\u00ac\u0001\u0000\u0000\u000078\u0005,\u0000\u0000"+
		"8\u0002\u0001\u0000\u0000\u00009:\u0005*\u0000\u0000:\u0004\u0001\u0000"+
		"\u0000\u0000;<\u0005=\u0000\u0000<\u0006\u0001\u0000\u0000\u0000=>\u0005"+
		"<\u0000\u0000>?\u0005>\u0000\u0000?\b\u0001\u0000\u0000\u0000@A\u0005"+
		"<\u0000\u0000A\n\u0001\u0000\u0000\u0000BC\u0005>\u0000\u0000C\f\u0001"+
		"\u0000\u0000\u0000DE\u0005<\u0000\u0000EF\u0005=\u0000\u0000F\u000e\u0001"+
		"\u0000\u0000\u0000GH\u0005>\u0000\u0000HI\u0005=\u0000\u0000I\u0010\u0001"+
		"\u0000\u0000\u0000JN\u0003/\u0017\u0000KL\u0003)\u0014\u0000LM\u0003/"+
		"\u0017\u0000MO\u0001\u0000\u0000\u0000NK\u0001\u0000\u0000\u0000OP\u0001"+
		"\u0000\u0000\u0000PN\u0001\u0000\u0000\u0000PQ\u0001\u0000\u0000\u0000"+
		"Q\u0012\u0001\u0000\u0000\u0000RS\u0007\u0000\u0000\u0000ST\u0007\u0001"+
		"\u0000\u0000TU\u0007\u0002\u0000\u0000UV\u0007\u0001\u0000\u0000VW\u0007"+
		"\u0003\u0000\u0000WX\u0007\u0004\u0000\u0000X\u0014\u0001\u0000\u0000"+
		"\u0000YZ\u0007\u0005\u0000\u0000Z[\u0007\u0006\u0000\u0000[\\\u0007\u0007"+
		"\u0000\u0000\\]\u0007\b\u0000\u0000]\u0016\u0001\u0000\u0000\u0000^_\u0007"+
		"\t\u0000\u0000_`\u0007\n\u0000\u0000`a\u0007\u0001\u0000\u0000ab\u0007"+
		"\u0006\u0000\u0000bc\u0007\u0001\u0000\u0000c\u0018\u0001\u0000\u0000"+
		"\u0000de\u0007\u000b\u0000\u0000ef\u0007\f\u0000\u0000fg\u0007\r\u0000"+
		"\u0000g\u001a\u0001\u0000\u0000\u0000hi\u0007\u0007\u0000\u0000ij\u0007"+
		"\u0006\u0000\u0000j\u001c\u0001\u0000\u0000\u0000kl\u0005;\u0000\u0000"+
		"l\u001e\u0001\u0000\u0000\u0000mn\u0007\r\u0000\u0000no\u0007\u0001\u0000"+
		"\u0000op\u0007\u0002\u0000\u0000pq\u0007\u0001\u0000\u0000qr\u0007\u0004"+
		"\u0000\u0000rs\u0007\u0001\u0000\u0000s \u0001\u0000\u0000\u0000tu\u0007"+
		"\u000e\u0000\u0000uv\u0007\f\u0000\u0000vw\u0007\u0000\u0000\u0000wx\u0007"+
		"\u0001\u0000\u0000xy\u0007\u0006\u0000\u0000yz\u0007\u0004\u0000\u0000"+
		"z\"\u0001\u0000\u0000\u0000{|\u0007\u000e\u0000\u0000|}\u0007\f\u0000"+
		"\u0000}~\u0007\u0004\u0000\u0000~\u007f\u0007\u0007\u0000\u0000\u007f"+
		"$\u0001\u0000\u0000\u0000\u0080\u0081\u0007\u000f\u0000\u0000\u0081\u0082"+
		"\u0007\u000b\u0000\u0000\u0082\u0083\u0007\u0002\u0000\u0000\u0083\u0084"+
		"\u0007\u0010\u0000\u0000\u0084\u0085\u0007\u0001\u0000\u0000\u0085\u0086"+
		"\u0007\u0000\u0000\u0000\u0086&\u0001\u0000\u0000\u0000\u0087\u0088\u0007"+
		"\f\u0000\u0000\u0088\u0089\u0007\u0010\u0000\u0000\u0089\u008a\u0007\u0002"+
		"\u0000\u0000\u008a\u008b\u0007\u0002\u0000\u0000\u008b(\u0001\u0000\u0000"+
		"\u0000\u008c\u008d\u0005.\u0000\u0000\u008d*\u0001\u0000\u0000\u0000\u008e"+
		"\u008f\u0005(\u0000\u0000\u008f,\u0001\u0000\u0000\u0000\u0090\u0091\u0005"+
		")\u0000\u0000\u0091.\u0001\u0000\u0000\u0000\u0092\u0094\u0007\u0011\u0000"+
		"\u0000\u0093\u0092\u0001\u0000\u0000\u0000\u0094\u0095\u0001\u0000\u0000"+
		"\u0000\u0095\u0093\u0001\u0000\u0000\u0000\u0095\u0096\u0001\u0000\u0000"+
		"\u0000\u0096\u009a\u0001\u0000\u0000\u0000\u0097\u0099\u0007\u0012\u0000"+
		"\u0000\u0098\u0097\u0001\u0000\u0000\u0000\u0099\u009c\u0001\u0000\u0000"+
		"\u0000\u009a\u0098\u0001\u0000\u0000\u0000\u009a\u009b\u0001\u0000\u0000"+
		"\u0000\u009b0\u0001\u0000\u0000\u0000\u009c\u009a\u0001\u0000\u0000\u0000"+
		"\u009d\u009f\u0007\u0012\u0000\u0000\u009e\u009d\u0001\u0000\u0000\u0000"+
		"\u009f\u00a0\u0001\u0000\u0000\u0000\u00a0\u009e\u0001\u0000\u0000\u0000"+
		"\u00a0\u00a1\u0001\u0000\u0000\u0000\u00a12\u0001\u0000\u0000\u0000\u00a2"+
		"\u00a6\u0005\'\u0000\u0000\u00a3\u00a5\t\u0000\u0000\u0000\u00a4\u00a3"+
		"\u0001\u0000\u0000\u0000\u00a5\u00a8\u0001\u0000\u0000\u0000\u00a6\u00a7"+
		"\u0001\u0000\u0000\u0000\u00a6\u00a4\u0001\u0000\u0000\u0000\u00a7\u00a9"+
		"\u0001\u0000\u0000\u0000\u00a8\u00a6\u0001\u0000\u0000\u0000\u00a9\u00aa"+
		"\u0005\'\u0000\u0000\u00aa4\u0001\u0000\u0000\u0000\u00ab\u00ad\u0007"+
		"\u0013\u0000\u0000\u00ac\u00ab\u0001\u0000\u0000\u0000\u00ad\u00ae\u0001"+
		"\u0000\u0000\u0000\u00ae\u00ac\u0001\u0000\u0000\u0000\u00ae\u00af\u0001"+
		"\u0000\u0000\u0000\u00af\u00b0\u0001\u0000\u0000\u0000\u00b0\u00b1\u0006"+
		"\u001a\u0000\u0000\u00b16\u0001\u0000\u0000\u0000\u0007\u0000P\u0095\u009a"+
		"\u00a0\u00a6\u00ae\u0001\u0006\u0000\u0000";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}