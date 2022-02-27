public interface ReCharTypes {
    string[] GetExampleMatch(Match matchedSoFar);
    ReCharTypes Add(Char chr);
    bool IsOptional {   get; }
    ReCharTypes SetOptional(bool val);
    bool IsMany {   get; }
    ReCharTypes SetMany(bool val);
    bool IsOpen {   get; }
    ReCharTypes SetOpen(bool val);
    ReCharTypes EndEdit();
}

public enum PlaceHolderType {
    OpenCircleBracket, CloseCircleBracket, Pipe, 
}
public enum TypeOfGroup{
    Normal, NonCapturing, LookAhead, LookBehind, NegativeLookAhead, NegativeLookBehind, Named, 
}
